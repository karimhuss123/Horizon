from sqlalchemy.orm import Session
from db.models import Security
from sqlalchemy import select

class SecurityRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_tickers_and_names(self):
        stmt = select(Security.id, Security.ticker, Security.name)
        rows = self.db.execute(stmt).mappings().all()
        return rows