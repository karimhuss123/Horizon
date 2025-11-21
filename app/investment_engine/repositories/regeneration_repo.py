from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException
from app.db.models import Basket, Regeneration
from app.db.utils.time import get_today_date, day_bounds_from_date

class RegenerationRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_regeneration(self, data, user_id):
        regeneration = Regeneration(
            user_id = user_id,
            basket_id = data["basket_id"],
            regeneration_user_prompt = data["regeneration_user_prompt"],
            initial_basket_name = data["initial_basket_name"],
            initial_basket_description = data["initial_basket_description"],
            initial_basket_holdings_list = data["initial_basket_holdings"],
            regenerated_name = data["name"],
            regenerated_description = data["description"],
            regenerated_holdings_list = data["holdings"]
        )
        self.db.add(regeneration)
        self.db.commit()
        return self.get_regeneration_by_id(regeneration.id, user_id)
    
    def get_regeneration_by_id(self, id: int, user_id: int):
        regeneration = (
            self.db.query(Regeneration)
            .filter(Regeneration.id == id)
            .first()
        )
        if regeneration is None:
            raise HTTPException(status_code=404, detail="Regeneration not found.")
        basket = regeneration.basket
        if basket is None or basket.deleted_at is not None or basket.user_id != user_id:
            raise HTTPException(status_code=404, detail="Regeneration not found.")
        return regeneration

    def get_basket_regenerations_today_count(self, user_id):
        today = get_today_date()
        day_start, day_end = day_bounds_from_date(today)
        return (
            self.db.query(Regeneration)
            .filter(
                Regeneration.user_id == user_id,
                Regeneration.created_at >= day_start,
                Regeneration.created_at < day_end
            )
            .count()
        )
    
    def accept_regeneration(self, id, user_id):
        regeneration_obj = self.get_regeneration_by_id(id, user_id)
        regeneration_obj.is_accepted = True
        self.db.commit()
        self.db.refresh(regeneration_obj)
        return regeneration_obj
        
        