from sqlalchemy.orm import Session
from services.ai_service import AIService
from repositories.basket_repo import BasketsRepo

class BasketService:
    def __init__(self, db: Session, ai=None):
        self.db = db
        self.ai = ai
        self.baskets = BasketsRepo(db)
    
    def generate_and_persist(self, user_prompt):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        data = self.ai.generate_basket_data(user_prompt)
        basket = self.baskets.create_draft_basket(data)
        return basket
    
    def regenerate(self, data):
        if not self.ai:
            raise RuntimeError("AIService is not initialized for BasketService.")
        basket_data = self.ai.regenerate_basket_data(data)
        return basket_data

    def get_all(self):
        baskets = self.baskets.get_all()
        return {"items": baskets[0], "total": baskets[1]}
    
    def get(self, id):
        return self.baskets.get(id)
    
    def accept_draft(self, id):
        return self.baskets.accept_draft(id)
    
    def delete(self, id):
        return self.baskets.delete(id)
    
    def edit(self, basket):
        return self.baskets.update(basket)