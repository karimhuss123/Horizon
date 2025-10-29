from sqlalchemy.orm import Session
from db.models import Security
from sqlalchemy import select

class SecurityRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_security(self, id):
        return self.db.query(Security).filter_by(id=id).first()
    
    def get_tickers_with_names(self, query):
        stmt = select(Security.id, Security.ticker, Security.name)
        if query:
            q = f"{str(query)}%"
            stmt = stmt.where(Security.ticker.ilike(q))
        stmt = stmt.order_by(Security.ticker)
        rows = self.db.execute(stmt).mappings().all()
        return rows