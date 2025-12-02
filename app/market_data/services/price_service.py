import yfinance as yf
from sqlalchemy.orm import Session
import pandas as pd
from app.db.utils.time import get_today_date, gap_in_days
from app.investment_engine.repositories.basket_repo import BasketRepo
from app.market_data.repositories.price_repo import PriceRepo
from app.market_data.repositories.security_repo import SecurityRepo

class PriceService:
    def __init__(self, db: Session):
        self.db = db
        self.prices = PriceRepo(db)
        self.securities = SecurityRepo(db)
        self.baskets = BasketRepo(db)
    
    def process_prices(self, basket_id, user_id):
        tickers_data = self.extract_tickers_data(user_id=user_id, basket_id=basket_id)
        tickers_list = list(tickers_data.keys())
        period = self.get_smallest_period(tickers_data.values())
        if period:
            # Add validation for DF (nulls, etc.)
            # Handle currencies. But not needed for chart, since we are just computing the change, but will be useful later
            prices_df = self.get_prices(tickers_list, period=period)
            rows = self.get_price_rows_with_ids(prices_df, tickers_data)
            self.prices.insert_rows(rows)
            return rows
        return
    
    def get_prices(self, tickers, period="1y"):
        df = yf.download(tickers, period=period)
        return df["Close"]
    
    def get_price_rows_with_ids(self, df, ticker_to_id):
        rows = (
            df
            .stack()
            .rename_axis(["date", "ticker"])
            .reset_index(name="close")
        )
        rows["security_id"] = rows["ticker"].map(ticker_to_id)
        rows["date"] = rows["date"].dt.date
        return rows.drop(columns="ticker").to_dict("records")
    
    def get_returns_grouped_by_date_df(self, security_ids, user_id):
        # Add period filter (maybe later, now doing filter in the frontend)
        prices = self.prices.get_prices_for_securities(security_ids)
        df = pd.DataFrame(
            [(p.security_id, p.date, p.close) for p in prices],
            columns=["security_id", "date", "close"]
        )
        df_pivot = df.pivot(index="date", columns="security_id", values="close")
        df_pivot = df_pivot.dropna()
        df_pivot = df_pivot.sort_index()
        return df_pivot.pct_change()
    
    def get_smallest_period(self, security_ids):
        if not security_ids:
            return "5d"
        today = get_today_date()
        last_dates = self.prices.get_last_price_dates(security_ids)
        if any(last_date is None for last_date in last_dates.values()):
            return "1y"
        gap_days_list = [gap_in_days(last_date, today) for last_date in last_dates.values()]
        max_gap = max(gap_days_list)
        return self.determine_period_from_gap(max_gap)

    def determine_period_from_gap(self, gap_days):
        if gap_days < 1:
            return
        if gap_days <= 6:
            return "5d"
        if gap_days <= 30:
            return "1mo"
        if gap_days <= 90:
            return "3mo"
        if gap_days <= 180:
            return "6mo"
        return "1y"
    
    def extract_tickers_data(self, user_id, basket_id=None, basket_obj=None):
        if not any([basket_id, basket_obj]):
            return
        if basket_id and not basket_obj:
            basket_obj = self.baskets.get(basket_id, user_id)
        return {holding.ticker: self.securities.get_security_id_for_ticker(holding.ticker) for holding in basket_obj.holdings}