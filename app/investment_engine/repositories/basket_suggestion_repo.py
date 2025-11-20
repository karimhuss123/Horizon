from sqlalchemy.orm import Session, selectinload
from db.models import Basket, Holding, Security, BasketStatus, BasketSuggestion
from fastapi import HTTPException
from db.utils.time import day_bounds_from_date, get_today_date, add_to_datetime

class BasketSuggestionRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_suggestions(self, basket_id, suggestions):
        for suggestion in suggestions:
            self.create_suggestion(basket_id, suggestion)
        return True

    def create_suggestion(self, basket_id, data):
        suggestion = BasketSuggestion(
            basket_id = basket_id,
            security_id = data["security_id"],
            news_id = data["news_id"],
            rationale = data["rationale"],
            score = data["score"],
            action = data["action"]
        )
        self.db.add(suggestion)
        self.db.commit()
        return suggestion
    
    def get_suggestions_for_basket_today(self, basket_id):
        today = get_today_date()
        day_start, day_end = day_bounds_from_date(today)
        return (
            self.db.query(BasketSuggestion)
            .filter(
                BasketSuggestion.basket_id == basket_id,
                BasketSuggestion.created_at >= day_start,
                BasketSuggestion.created_at < day_end
            )
            .all()
        )