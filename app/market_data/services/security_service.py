from sqlalchemy.orm import Session
from app.market_data.repositories.security_repo import SecurityRepo

class SecurityService:
    def __init__(self, db: Session):
        self.db = db
        self.securities = SecurityRepo(db)
    
    def get_tickers_with_names(self, query):
        return self.securities.get_tickers_with_names(query)
    
    def get_securities(self, ids):
        return self.securities.get_securities(ids)