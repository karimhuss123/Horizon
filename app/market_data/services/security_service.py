from sqlalchemy.orm import Session
from market_data.repositories.security_repo import SecurityRepo

class SecurityService:
    def __init__(self, db: Session):
        self.db = db
        self.securities = SecurityRepo(db)
    
    def get_tickers_and_names(self):
        return self.securities.get_tickers_and_names()