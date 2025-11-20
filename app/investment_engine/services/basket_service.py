from sqlalchemy.orm import Session
from investment_engine.services.selector_service import SelectorService
from investment_engine.services.theme_service import ThemeService
from investment_engine.repositories.basket_repo import BasketRepo
from investment_engine.repositories.regeneration_repo import RegenerationRepo
from investment_engine.repositories.basket_suggestion_repo import BasketSuggestionRepo
from investment_engine.utils.fingerprint import compute_basket_fingerprint
from core.errors.messages import messages
from core.config import settings
from fastapi import HTTPException, status
import json

class BasketService:
    def __init__(self, db: Session, ai=None):
        self.db = db
        self.ai = ai
        self.baskets = BasketRepo(db)
        self.regenerations = RegenerationRepo(db)
        self.suggestions = BasketSuggestionRepo(db)
    
    def generate_basket(self, user_prompt, user_id):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        if self.baskets.get_baskets_created_today_count(user_id) >= settings.BASKET_GENERATION_DAILY_LIMIT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.baskets_generation_daily_limit})
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        criteria = self.ai.generate_intent_query(user_prompt)
        if criteria.get("error") == "invalid_user_prompt":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.meaningless_user_prompt})
        candidate_securities_ids = selector_svc.screen(criteria)
        embedded_query = theme_svc.get_embedded_query(criteria)
        hits = theme_svc.vector_search_within_candidates(query_vec=embedded_query, include_ids=candidate_securities_ids, limit=criteria["count"])
        weighted_holdings = selector_svc.assign_hybrid_weights(securities=hits)
        weighted_holdings_with_rationale = self.ai.generate_holding_rationales(criteria, weighted_holdings)
        data = {
            "user_id": user_id,
            "user_prompt": user_prompt,
            "embedded_query": embedded_query,
            "criteria": criteria,
            "holdings": weighted_holdings_with_rationale
        }
        basket = self.baskets.create_draft_basket(data)
        fingerprint = compute_basket_fingerprint(basket)
        self.baskets.update_basket_fingerprint(basket.id, fingerprint, user_id)
        return basket
    
    def regenerate_basket(self, regen_data, user_id):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        if self.regenerations.get_basket_regenerations_today_count(user_id) >= settings.BASKET_REGENERATION_DAILY_LIMIT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.baskets_regeneration_daily_limit})
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        basket = self.baskets.get(id=regen_data.id, user_id=user_id) # validate basket existence
        criteria = self.ai.regenerate_intent_query(regen_data)
        if criteria.get("error") == "invalid_user_prompt":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.meaningless_user_prompt})
        candidate_securities_ids = selector_svc.screen(criteria)
        embedded_query = theme_svc.get_embedded_query(criteria)
        hits = theme_svc.vector_search_within_candidates(query_vec=embedded_query, include_ids=candidate_securities_ids, limit=criteria["count"])
        weighted_holdings = selector_svc.assign_hybrid_weights(securities=hits)
        weighted_holdings_with_rationale = self.ai.generate_holding_rationales(criteria, weighted_holdings)
        data = {
            "basket_id": basket.id,
            "regeneration_user_prompt": regen_data.user_prompt,
            "initial_basket_name": regen_data.name,
            "initial_basket_description": regen_data.description,
            "initial_basket_holdings": [json.loads(h.json()) for h in regen_data.holdings],
            "name": criteria["name"],
            "description": criteria["theme_summary"],
            "holdings": weighted_holdings_with_rationale
        }
        regeneration = self.regenerations.create_regeneration(data, user_id)
        data["id"] = regeneration.id
        return data

    def get_all_baskets(self, user_id):
        baskets = self.baskets.get_all(user_id=user_id)
        return {"items": baskets[0], "total": baskets[1]}
    
    def get_basket(self, id, user_id):
        return self.baskets.get(id, user_id)
    
    def accept_draft(self, id, user_id):
        return self.baskets.accept_draft(id, user_id)
    
    def delete_basket(self, id, user_id):
        return self.baskets.delete(id, user_id)
    
    def edit_basket(self, basket, user_id):
        existing_basket = self.baskets.get(id=basket.id, user_id=user_id) # validates basket
        new_fingerprint = compute_basket_fingerprint(basket)
        if existing_basket.basket_fingerprint == new_fingerprint:
            return self.baskets.update(basket=basket, user_id=user_id, metadata=None, description_embedding=None)
        theme_svc = ThemeService(self.db, self.ai.client)
        metadata = self.ai.generate_basket_metadata(basket)
        description_embedding = theme_svc.get_embedded_query({
            "theme_summary": basket.description,
            "keywords": metadata.get("keywords", []),
            "sectors": metadata.get("sectors", [])
        })
        updated = self.baskets.update(basket=basket, user_id=user_id, metadata=metadata, description_embedding=description_embedding)
        self.baskets.update_basket_fingerprint(id=basket.id, fingerprint=new_fingerprint, user_id=user_id)
        return updated
    
    def accept_regeneration(self, regeneration_id, user_id):
        return self.regenerations.accept_regeneration(regeneration_id, user_id)