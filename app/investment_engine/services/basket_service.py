from sqlalchemy.orm import Session
from investment_engine.services.selector_service import SelectorService
from investment_engine.services.theme_service import ThemeService
from investment_engine.services.similarity_service import SimilarityService
from investment_engine.repositories.basket_repo import BasketRepo
from market_data.services.news_service import NewsService

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
        hits = theme_svc.vector_search_within_candidates(query_vec=embedded_query, include_ids=candidate_securities_ids)
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
        hits = theme_svc.vector_search_within_candidates(query_vec=embedded_query, include_ids=candidate_securities_ids)
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
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        news_svc = NewsService(self.db, self.ai.client)
        sim_svc = SimilarityService(self.db)
        basket = self.baskets.get(basket_id)
        candidate_ids = selector_svc.screen({
            "min_market_cap_usd": basket.market_cap_min_usd,
            "max_market_cap_usd": basket.market_cap_max_usd,
            "sectors": basket.sectors,
            "regions": basket.regions
        })
        basket_security_ids = self.baskets.get_basket_security_ids(basket_id)
        add_hits = theme_svc.vector_search_within_candidates(basket.description_embedding, include_ids=candidate_ids, exclude_ids=basket_security_ids)
        news_svc.process_news_for_securities(add_hits)
        top_5_suggestions = sim_svc.get_top_k_suggestions(basket.description_embedding, add_hits, k=5)
        top_5_suggestions_with_rationales = self.ai.generate_suggestion_rationales(basket, top_5_suggestions)
        return top_5_suggestions_with_rationales