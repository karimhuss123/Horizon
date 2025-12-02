from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.investment_engine.services.selector_service import SelectorService
from app.investment_engine.services.theme_service import ThemeService
from app.investment_engine.repositories.basket_repo import BasketRepo
from app.investment_engine.repositories.regeneration_repo import RegenerationRepo
from app.investment_engine.repositories.basket_suggestion_repo import BasketSuggestionRepo
from app.investment_engine.utils.fingerprint import compute_basket_fingerprint
from app.market_data.services.price_service import PriceService
from app.market_data.repositories.security_repo import SecurityRepo
from app.core.errors.messages import messages
from app.core.config import settings

class BasketService:
    def __init__(self, db: Session, ai=None):
        self.db = db
        self.ai = ai
        self.baskets = BasketRepo(db)
        self.regenerations = RegenerationRepo(db)
        self.suggestions = BasketSuggestionRepo(db)
        self.securities = SecurityRepo(db)
    
    def generate_basket(self, user_prompt, user_id):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        if self.baskets.get_baskets_created_today_count(user_id) >= settings.BASKET_GENERATION_DAILY_LIMIT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.baskets_generation_daily_limit})
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        price_svc = PriceService(self.db)
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
        price_svc.process_prices(basket_id=basket.id, user_id=user_id)
        return basket
    
    def regenerate_basket(self, regen_data, user_id):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        if self.regenerations.get_basket_regenerations_today_count(user_id) >= settings.BASKET_REGENERATION_DAILY_LIMIT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.baskets_regeneration_daily_limit})
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        basket = self.baskets.get(id=regen_data["basket_id"], user_id=user_id) # validate basket existence
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
            "regeneration_user_prompt": regen_data["user_prompt"],
            "initial_basket_name": regen_data["name"],
            "initial_basket_description": regen_data["description"],
            "initial_basket_holdings": [h for h in regen_data["holdings"]],
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
        price_svc = PriceService(self.db)
        metadata = self.ai.generate_basket_metadata(basket)
        description_embedding = theme_svc.get_embedded_query({
            "theme_summary": basket.description,
            "keywords": metadata.get("keywords", []),
            "sectors": metadata.get("sectors", [])
        })
        updated = self.baskets.update(basket=basket, user_id=user_id, metadata=metadata, description_embedding=description_embedding)
        price_svc.process_prices(basket_id=updated.id, user_id=user_id)
        self.baskets.update_basket_fingerprint(id=basket.id, fingerprint=new_fingerprint, user_id=user_id)
        return updated
    
    def accept_regeneration(self, regeneration_id, user_id):
        return self.regenerations.accept_regeneration(regeneration_id, user_id)
    
    def reject_regeneration(self, regeneration_id, user_id):
        return self.regenerations.reject_regeneration(regeneration_id, user_id)
    
    def get_regeneration_for_basket(self, basket_id, user_id):
        basket = self.baskets.get(basket_id, user_id)
        regeneration_obj = self.regenerations.get_pending_regeneration_for_basket(basket_id, user_id)
        if regeneration_obj:
            return {
                "id": regeneration_obj.id,
                "name": regeneration_obj.regenerated_name,
                "description": regeneration_obj.regenerated_description,
                "holdings": regeneration_obj.regenerated_holdings_list
            }
    
    def get_performance(self, basket_id, user_id):
        price_svc = PriceService(self.db)
        basket = self.baskets.get(basket_id, user_id)
        security_ids = self.baskets.get_basket_security_ids(basket.id, user_id)
        returns_df = price_svc.get_returns_grouped_by_date_df(
            security_ids=security_ids,
            user_id=user_id
        )
        weights = self._build_weights(basket)
        weight_vector = [weights[col] for col in returns_df.columns]
        weighted_returns = returns_df * weight_vector
        basket_daily_return = weighted_returns.sum(axis=1)
        basket_value_series = settings.CHART_INITIAL_VALUE * (1 + basket_daily_return).cumprod()
        
        labels = [d.strftime("%Y-%m-%d") for d in basket_value_series.index]
        values = basket_value_series.round(2).tolist()
        return {"labels": labels, "values": values}
    
    def _build_weights(self, basket):
        return {h.security_id: h.weight_pct / 100 for h in basket.holdings}
