from sqlalchemy.orm import Session
from db.models import LoginCode, User
from db.utils.time import current_datetime_et, add_to_datetime
from core.config import settings
from db.utils.time import get_today_date, day_bounds_from_date

class LoginCodeRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def invalidate_old_login_codes(self, user_id):
        now = current_datetime_et()
        (
            self.db.query(LoginCode)
            .filter(
                LoginCode.user_id == user_id,
                LoginCode.used_at.is_(None),
                LoginCode.expires_at > now
            )
            .update(
                {
                    LoginCode.expires_at: now,
                    LoginCode.used_at: now
                },
                synchronize_session=False
            )
        )
        self.db.commit()
    
    def generate_new_login_code(self, user_id, code_hash):
        now = current_datetime_et()
        login_code = LoginCode(
            user_id=user_id,
            code_hash=code_hash,
            expires_at=add_to_datetime(dt=now, minutes=settings.LOGIN_CODE_MINUTES_TO_EXPIRY)
        )
        self.db.add(login_code)
        self.db.commit()
        return login_code
    
    def get_valid_login_code_for_user(self, user_id):
        now = current_datetime_et()
        return (
            self.db.query(LoginCode)
            .filter(
                LoginCode.user_id == user_id,
                LoginCode.used_at.is_(None),
                LoginCode.expires_at > now
            ).first()
        )
    
    def increment_login_code_attempts(self, logincode_id):
        (
            self.db.query(LoginCode)
            .filter(LoginCode.id == logincode_id)
            .update(
                {
                    LoginCode.attempts: LoginCode.attempts + 1
                },
                synchronize_session=False
            )
        )
        self.db.commit()
    
    def set_login_code_as_used(self, logincode_id):
        now = current_datetime_et()
        (
            self.db.query(LoginCode)
            .filter(LoginCode.id == logincode_id)
            .update(
                {
                    LoginCode.used_at: now
                },
                synchronize_session=False
            )
        )
        self.db.commit()
    
    def get_login_code_count_today(self, user_id):
        today = get_today_date()
        day_start, day_end = day_bounds_from_date(today)
        return (
            self.db.query(LoginCode)
            .filter(
                LoginCode.user_id == user_id,
                LoginCode.created_at >= day_start,
                LoginCode.created_at < day_end
            )
            .count()
        )