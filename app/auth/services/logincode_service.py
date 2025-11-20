from sqlalchemy.orm import Session
from auth.repositories.logincode_repo import LoginCodeRepo
from auth.utils.auth_utils import generate_random_code, generate_code_hash
from core.config import settings
from fastapi import HTTPException, status
from core.errors.messages import messages

class LoginCodeService:
    def __init__(self, db: Session):
        self.db = db
        self.login_codes = LoginCodeRepo(db)
    
    def generate_code(self, user_id):
        if self.login_codes.get_login_code_count_today(user_id) >= settings.LOGIN_CODE_DAILY_LIMIT:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": messages.auth_too_many_login_codes})
        self.login_codes.invalidate_old_login_codes(user_id)
        code = generate_random_code()
        code_hash = generate_code_hash(code)
        self.login_codes.generate_new_login_code(user_id, code_hash)
        return code
    
    def validate_code(self, user_id, code):
        valid_code = self.login_codes.get_valid_login_code_for_user(user_id)
        if not valid_code or valid_code.attempts >= settings.LOGIN_CODE_VERIFICATION_MAX_ATTEMPTS:
            return False
        self.login_codes.increment_login_code_attempts(valid_code.id)
        attempted_code_hash = generate_code_hash(code)
        if attempted_code_hash != valid_code.code_hash:
            return False
        self.login_codes.set_login_code_as_used(valid_code.id)
        return True