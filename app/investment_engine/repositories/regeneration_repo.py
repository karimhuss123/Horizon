from sqlalchemy.orm import Session, selectinload
from db.models import Basket, Regeneration
from fastapi import HTTPException
import json

class RegenerationRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_regeneration(self, data, user_id):
        regeneration = Regeneration(
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
    
    def get_regeneration_by_id(self, id, user_id):
        regeneration = self.db.query(Regeneration).filter_by(id=id).first()
        basket = regeneration.basket
        if user_id != basket.user_id:
            return RuntimeError("Regeneration not found.")
        return regeneration
    
    def accept_regeneration(self, id, user_id):
        regeneration_obj = self.get_regeneration_by_id(id, user_id)
        regeneration_obj.is_accepted = True
        self.db.commit()
        self.db.refresh(regeneration_obj)
        return regeneration_obj
        
        