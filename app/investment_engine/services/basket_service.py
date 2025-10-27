from sqlalchemy.orm import Session
from investment_engine.services.selector_service import SelectorService
from investment_engine.services.theme_service import ThemeService
from investment_engine.repositories.basket_repo import BasketRepo
import json

class BasketService:
    def __init__(self, db: Session, ai=None):
        self.db = db
        self.ai = ai
        self.baskets = BasketRepo(db)
    
    def generate_basket(self, user_prompt):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        criteria = self.ai.generate_intent_query(user_prompt)
        candidate_securities_ids = selector_svc.screen(criteria)
        embedded_query = theme_svc.get_embedded_query(criteria)
        hits = theme_svc.vector_search_within_candidates(query_vec=embedded_query, candidate_ids=candidate_securities_ids)
        weighted_holdings = selector_svc.assign_hybrid_weights(securities=hits)
        weighted_holdings_with_rationale = self.ai.generate_holding_rationales(criteria, weighted_holdings)
        data = {
            "user_prompt": user_prompt,
            "embedded_query": embedded_query,
            "criteria": criteria,
            "holdings": weighted_holdings_with_rationale
        }
        basket = self.baskets.create_draft_basket(data)
        return basket
    
    def regenerate_basket(self, regen_data):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        criteria = self.ai.regenerate_intent_query(regen_data)
        candidate_securities_ids = selector_svc.screen(criteria)
        embedded_query = theme_svc.get_embedded_query(criteria)
        hits = theme_svc.vector_search_within_candidates(query_vec=embedded_query, candidate_ids=candidate_securities_ids)
        weighted_holdings = selector_svc.assign_hybrid_weights(securities=hits)
        weighted_holdings_with_rationale = self.ai.generate_holding_rationales(criteria, weighted_holdings)
        data = {
            "name": criteria["name"],
            "description": criteria["theme_summary"],
            "holdings": weighted_holdings_with_rationale
        }
        return data

    def get_all_baskets(self):
        baskets = self.baskets.get_all()
        return {"items": baskets[0], "total": baskets[1]}
    
    def get_basket(self, id):
        return self.baskets.get(id)
    
    def accept_draft(self, id):
        return self.baskets.accept_draft(id)
    
    def delete_basket(self, id):
        return self.baskets.delete(id)
    
    def edit_basket(self, basket):
        theme_svc = ThemeService(self.db, self.ai.client)
        metadata = self.ai.generate_basket_metadata(basket)        
        embedded_query = theme_svc.get_embedded_query({
            "theme_summary": basket.description,
            "keywords": metadata.get("keywords", []),
            "sectors": metadata.get("sectors", [])
        })    
        return self.baskets.update(basket, metadata, embedded_query)
    
    def get_basket_suggestions(self, basket_id):
        basket = self.baskets.get(basket_id)
        suggestions = self.ai.generate_basket_suggestions(basket)
        return suggestions.get('data', [])