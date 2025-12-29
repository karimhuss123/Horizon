import yfinance as yf
from sqlalchemy.orm import Session
from app.market_data.services.security_service import SecurityService
from app.market_data.repositories.fundamentals_repo import FundamentalsRepo

class FundamentalsService:
    def __init__(self, db: Session):
        self.db = db
        self.fundamentals = FundamentalsRepo(db)
    
    def get_fundamentals(self, security_ids):
        # here, return the most recent fundamentals available
        # if most recent fundamentals are out of date, start a background job for processing...
        # always return immediately with most recent fundamentals available
        # (maybe) add something to say that they are currently being updated...
        
        # call this function only
        fundamentals_map = self.fundamentals.get_latest_fundamentals_by_security_ids(security_ids)
        outdated_security_ids = self.fundamentals.get_outdated_fundamentals(security_ids)
        
        return fundamentals_map, outdated_security_ids
    
    def process_fundamentals(self, security_ids):
        sec_svc = SecurityService(self.db)
        securities = sec_svc.get_securities(security_ids)
        id_to_sec = {s.id: s for s in securities}
        outdated_tickers = [id_to_sec[sid].ticker for sid in security_ids if sid in id_to_sec]
        fundamentals_data = self.fetch_fundamentals(outdated_tickers, id_to_sec)
        self.fundamentals.create_fundamentals(fundamentals_data)
    
    def fetch_fundamentals(self, tickers_list, id_to_sec):
        if not tickers_list or not id_to_sec:
            return
        ticker_to_id = {s.ticker: s.id for s in id_to_sec.values()}
        yt = yf.Tickers(" ".join(tickers_list))
        out = []
        for ticker, ticker_obj in yt.tickers.items():
            security_id = ticker_to_id.get(ticker)
            if security_id is None:
                continue
            info = ticker_obj.info
            out.append({
                "security_id": security_id,
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "dividend_rate": info.get("trailingAnnualDividendRate"),
                "dividend_yield": info.get("trailingAnnualDividendYield"),
            })
        return out
