from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import Security

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
    
    def get_security_id_for_ticker(self, ticker):
        security_obj = (
            self.db.query(Security)
            .filter(Security.ticker == ticker)
        ).first()
        if not security_obj:
            return RuntimeError(f'Ticker "{ticker}" does not exist.')
        return security_obj.id