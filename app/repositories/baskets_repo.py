from sqlalchemy.orm import Session
from db.models import Basket, Holding, Security, BasketStatus

class BasketsRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_draft_basket(self, data):
        basket = Basket(
            name = data["basket_name"],
            prompt_text = data["user_prompt"],
            description = data["thesis"],
            status = BasketStatus.DRAFT
        )
        
        self.db.add(basket)
        self.db.flush()
        
        for h in data.get("holdings", []):
            security = (
                self.db.query(Security)
                .filter(Security.ticker == h["ticker"])
                .one_or_none()
            )

            if not security:
                security = Security(
                    ticker=h["ticker"],
                    name=h["name"],
                    # exchange=h.get("exchange"),
                    # country=h.get("country"),
                    # sector=h.get("sector"),
                    # currency="USD",
                )
                self.db.add(security)
                self.db.flush()

            holding = Holding(
                basket_id=basket.id,
                security_id=security.id,
                weight_pct=h["weight_pct"],
                rationale=h.get("rationale"),
            )
            self.db.add(holding)

        self.db.commit()
        self.db.refresh(basket)
        
        return basket
    
    def get_all():
        pass