from sqlalchemy.orm import Session, selectinload
from db.models import Basket, Holding, Security, BasketStatus
from fastapi import HTTPException

class BasketRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def create_draft_basket(self, data):
        basket = Basket(
            user_id = data["user_id"],
            initial_user_prompt = data["user_prompt"],
            name = data["criteria"]["name"],
            description = data["criteria"]["theme_summary"],
            keywords = list(data["criteria"]["keywords"]),
            sectors = list(data["criteria"]["sectors"]),
            regions = list(data["criteria"]["regions"]),
            market_cap_min_usd = data["criteria"]["min_market_cap_usd"],
            market_cap_max_usd = data["criteria"]["max_market_cap_usd"],
            description_embedding = data["embedded_query"],
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
    
    def get_all(self, user_id):
        baskets = (
            self.db.query(Basket)
            .filter_by(user_id=user_id)
            .options(
                selectinload(Basket.holdings).selectinload(Holding.security)
            )
            .order_by(Basket.id.desc())
            .all()
        )
        return baskets, len(baskets)
    
    def get(self, id, user_id):
        basket = (
            self.db.query(Basket)
            .filter_by(id=id, user_id=user_id)
            .options(
                selectinload(Basket.holdings).selectinload(Holding.security)
            ).first()
        )
        if not basket:
            raise HTTPException(status_code=404, detail="Basket not found")
        return basket
    
    def get_basket_security_ids(self, id, user_id):
        basket = self.get(id, user_id)
        seen = set()
        out = []
        for h in basket.holdings:
            sid = h.security.id
            if sid is not None and sid not in seen:
                seen.add(sid)
                out.append(sid)
        return out
    
    def accept_draft(self, id, user_id):
        basket = self.get(id, user_id)
        if not basket:
            return RuntimeError("Basket does not exist.")
        basket.status = BasketStatus.ACTIVE
        self.db.commit()
        self.db.refresh(basket)
        return basket
    
    def delete(self, id, user_id):
        basket = self.get(id, user_id)
        if not basket:
            return RuntimeError("Basket does not exist.")
        self.db.delete(basket)
        self.db.commit()
    
    def update(self, basket, metadata, user_id, description_embedding = None):
        basket_obj = self.get(basket.id, user_id)
        if not basket_obj:
            raise RuntimeError("Basket does not exist.")
        try:
            basket_obj.name = basket.name
            basket_obj.description = basket.description
            basket_obj.keywords = metadata.get('keywords', [])
            basket_obj.sectors = metadata.get('sectors', [])
            basket_obj.regions = metadata.get('regions', [])
            basket_obj.market_cap_min_usd = metadata.get('min_market_cap_usd', None)
            basket_obj.market_cap_max_usd = metadata.get('max_market_cap_usd', None)
            basket_obj.status = BasketStatus(basket.status)
            if description_embedding:
                basket_obj.description_embedding = description_embedding
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