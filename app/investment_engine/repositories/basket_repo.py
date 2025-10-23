from sqlalchemy.orm import Session, selectinload
from db.models import Basket, Holding, Security, BasketStatus

class BasketRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_draft_basket(self, data):
        basket = Basket(
            prompt_text = data["user_prompt"],
            name = data["criteria"]["name"],
            description = data["criteria"]["theme_summary"],
            status = BasketStatus.DRAFT
        )
        self.db.add(basket)
        self.db.flush()
        
        for h in data.get("holdings", []):            
            holding = Holding(
                basket_id=basket.id,
                security_id=h["id"],
                weight_pct=h["weight_pct"],
                rationale=h["rationale"],
            )
            self.db.add(holding)

        self.db.commit()
        self.db.refresh(basket)
        
        return (
            self.db.query(Basket)
            .options(
                selectinload(Basket.holdings).selectinload(Holding.security)
            )
            .get(basket.id)
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
            return RuntimeError("Basket does not exist.")
        basket.status = BasketStatus.ACTIVE
        self.db.commit()
        self.db.refresh(basket)
        return basket
    
    def delete(self, id):
        basket = self.get(id)
        if not basket:
            return RuntimeError("Basket does not exist.")
        self.db.delete(basket)
        self.db.commit()
        return
    
    def update(self, basket):
        basket_obj = self.get(basket.id)
        if not basket_obj:
            raise RuntimeError("Basket does not exist.")
        
        try:
            basket_obj.name = basket.name
            basket_obj.description = basket.description
            basket_obj.status = BasketStatus(basket.status)
            
            self.db.commit()
            self.db.flush()
            
            basket_obj.holdings = []
            
            for h in basket.holdings:
                ticker = h.ticker
                if not ticker:
                    raise ValueError("Holding missing ticker.")
                security = (
                    self.db.query(Security)
                    .filter(Security.ticker == ticker)
                    .one_or_none()
                )
                if not security:
                    return RuntimeError(f'Ticker "{ticker}" does not exist.')

                holding = Holding(
                    basket_id=basket_obj.id,
                    security_id=security.id,
                    weight_pct=h.weight_pct,
                    rationale=h.rationale,
                )
                self.db.add(holding)

            self.db.commit()
            self.db.refresh(basket_obj)
            return basket_obj
        except Exception:
            self.db.rollback()
            raise