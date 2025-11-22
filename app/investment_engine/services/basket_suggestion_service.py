from sqlalchemy.orm import Session
from app.investment_engine.services.selector_service import SelectorService
from app.investment_engine.services.theme_service import ThemeService
from app.investment_engine.services.similarity_service import SimilarityService
from app.investment_engine.repositories.basket_repo import BasketRepo
from app.investment_engine.repositories.basket_suggestion_repo import BasketSuggestionRepo
from app.market_data.services.news_service import NewsService

class BasketSuggestionService:
    def __init__(self, db: Session, ai=None):
        self.db = db
        self.ai = ai
        self.baskets = BasketRepo(db)
        self.suggestions = BasketSuggestionRepo(db)
    
    def generate_basket_suggestions(self, basket_id, user_id):
        basket = self.baskets.get(basket_id, user_id)
        todays_suggestions_for_basket = self.suggestions.get_suggestions_for_basket_today(basket.id)
        if todays_suggestions_for_basket:
            return self._build_suggestions_list(todays_suggestions_for_basket)
        selector_svc = SelectorService(self.db)
        theme_svc = ThemeService(self.db, self.ai.client)
        news_svc = NewsService(self.db, self.ai.client)
        sim_svc = SimilarityService(self.db)
        candidate_ids = selector_svc.screen({
            "min_market_cap_usd": basket.market_cap_min_usd,
            "max_market_cap_usd": basket.market_cap_max_usd,
            "sectors": basket.sectors,
            "regions": basket.regions
        })
        basket_security_ids = self.baskets.get_basket_security_ids(basket_id, user_id)
        add_hits = theme_svc.vector_search_within_candidates(query_vec=basket.description_embedding, include_ids=candidate_ids, exclude_ids=basket_security_ids)
        news_svc.process_news_for_securities(add_hits)
        top_k_suggestions = sim_svc.get_top_k_suggestions(basket.description_embedding, add_hits)
        # Later: check if suggestion exists with same security id and news id for basket, if so then just use it instead of generating rationale again...
        top_k_suggestions_with_rationales = self.ai.generate_suggestion_rationales(basket, top_k_suggestions)
        self.suggestions.create_suggestions(basket.id, top_k_suggestions)
        return top_k_suggestions_with_rationales
    
    def get_basket_suggestions(self, basket_id, user_id):
        basket = self.baskets.get(basket_id, user_id)
        todays_suggestions_for_basket = self.suggestions.get_suggestions_for_basket_today(basket.id)
        if not todays_suggestions_for_basket:
            return []
        return self._build_suggestions_list(todays_suggestions_for_basket)

    def _build_suggestions_list(self, suggestions):
        return [
                {
                    "security_id": suggestion.security_id,
                    "ticker": suggestion.security.ticker,
                    "name": suggestion.security.name,
                    "rationale": suggestion.rationale,
                    "action": suggestion.action,
                    "source_url": suggestion.news.url
                }
                for suggestion in suggestions
            ]