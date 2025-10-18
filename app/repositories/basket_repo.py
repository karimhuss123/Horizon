from sqlalchemy.orm import Session, selectinload
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
        
        return (
            self.db.query(Basket)
            .options(
                selectinload(Basket.holdings).selectinload(Holding.security)
            )
            .get(data["id"] if "id" in data else basket.id)
        )
    
    def get_all(self):
        baskets = (
            self.db.query(Basket)
            .options(
                selectinload(Basket.holdings).selectinload(Holding.security)
            )
            .order_by(Basket.id.desc())
            .all()
        )
        return baskets, len(baskets)
    
    def get(self, id):
        return (
            self.db.query(Basket)
            .filter_by(id=id)
            .options(
                selectinload(Basket.holdings).selectinload(Holding.security)
            ).first()
        )
    
    def accept_draft(self, id):
        basket = self.get(id)
        if not basket:
            return None
        basket.status = BasketStatus.ACCEPTED
        self.db.commit()
        self.db.refresh(basket)
        return basket
    
    def reject_draft(self, id):
        basket = self.get(id)
        if not basket:
            return None
        basket.status = BasketStatus.REJECTED
        self.db.commit()
        self.db.refresh(basket)
        return basket