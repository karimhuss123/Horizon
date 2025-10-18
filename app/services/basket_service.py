from sqlalchemy.orm import Session
from services.ai_service import AIService
from repositories.baskets_repo import BasketsRepo

class BasketService:
    def __init__(self, db: Session, ai: AIService):
        self.db = db
        self.ai = ai
        self.baskets = BasketsRepo(db)
    
    def generate_and_persist(self, user_prompt):
        data = self.ai.generate_basket_data(user_prompt)
        basket = self.baskets.create_draft_basket(data)
        return basket