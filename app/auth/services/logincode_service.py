from sqlalchemy.orm import Session
from auth.repositories.user_repo import UserRepo
from auth.repositories.logincode_repo import LoginCodeRepo
from auth.utils.auth_utils import generate_random_code, generate_code_hash
from core.config import settings

class LoginCodeService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepo(db)
        self.logincode_repo = LoginCodeRepo(db)
    
    def generate_code(self, user_id):
        self.logincode_repo.invalidate_old_login_codes(user_id)
        code = generate_random_code()
        code_hash = generate_code_hash(code)
        self.logincode_repo.generate_new_login_code(user_id, code_hash)
        return code
    
    def validate_code(self, user_id, code):
        valid_code = self.logincode_repo.get_valid_login_code_for_user(user_id)
        if not valid_code or valid_code.attempts >= settings.LOGIN_CODE_VERIFICATION_MAX_ATTEMPTS:
            return False
        self.logincode_repo.increment_login_code_attempts(valid_code.id)
        attempted_code_hash = generate_code_hash(code)
        if attempted_code_hash != valid_code.code_hash:
            return False
        self.logincode_repo.set_login_code_as_used(valid_code.id)
        return True