from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db.models import Price

class PriceRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def insert_rows(self, rows):
        stmt = insert(Price).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["security_id", "date"],
            set_={"close": stmt.excluded.close}
        )
        self.db.execute(stmt)
        self.db.commit()
        return
    
    def get_prices_for_securities(self, security_ids):
        return (
            self.db.query(Price)
            .filter(Price.security_id.in_(security_ids))
        ).all()
    
    def get_last_price_dates(self, security_ids):
        rows = (
            self.db.query(Price.security_id, func.max(Price.date))
            .filter(Price.security_id.in_(security_ids))
            .group_by(Price.security_id)
            .all()
        )
        result = {sid: None for sid in security_ids}
        for sid, last_date in rows:
            result[sid] = last_date
        return result
    