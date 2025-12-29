from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.db.models import Fundamental
from app.db.utils.time import get_today_date

class FundamentalsRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_outdated_fundamentals(self, security_ids):
        today = get_today_date()
        today_ids = {
            row.security_id
            for row in self.db.query(Fundamental.security_id)
            .filter(
                Fundamental.security_id.in_(security_ids),
                Fundamental.as_of == today
            )
            .distinct()
            .all()
        }
        return list(set(security_ids) - today_ids)

    def create_fundamentals(self, data):
        out = []
        for item in data:
            fundamental = Fundamental(
                security_id = item["security_id"],
                open = item["open"],
                day_high = item["day_high"],
                day_low = item["day_low"],
                market_cap = item["market_cap"],
                pe_ratio = item["pe_ratio"],
                fifty_two_week_high = item["fifty_two_week_high"],
                fifty_two_week_low = item["fifty_two_week_low"],
                dividend_rate = item["dividend_rate"],
                dividend_yield = item["dividend_yield"],
                as_of = get_today_date()
            )
            self.db.add(fundamental)
            out.append(fundamental)
        self.db.commit()
        return out

    def get_latest_fundamentals_by_security_ids(self, security_ids):
        if not security_ids:
            return {}
        subq = (
            self.db.query(
                Fundamental.security_id,
                func.max(Fundamental.as_of).label("max_as_of"),
            )
            .filter(Fundamental.security_id.in_(security_ids))
            .group_by(Fundamental.security_id)
            .subquery()
        )
        rows = (
            self.db.query(Fundamental)
            .join(
                subq,
                and_(
                    Fundamental.security_id == subq.c.security_id,
                    Fundamental.as_of == subq.c.max_as_of,
                ),
            )
            .all()
        )
        return {f.security_id: f for f in rows}
