from sqlalchemy.orm import Session
from auth.utils.auth_utils import validate_user_email, send_login_code_email
from auth.repositories.user_repo import UserRepo
from auth.services.logincode_service import LoginCodeService

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepo(db)
    
    def process_code_request(self, email, background_tasks):
        logincode_svc = LoginCodeService(self.db)
        normalized_email = validate_user_email(email)
        user = self.user_repo.get_or_create_user(normalized_email)
        code = logincode_svc.generate_code(user.id)
        background_tasks.add_task(send_login_code_email, code, user.email)
    
    def verify_code(self, email, code):
        logincode_svc = LoginCodeService(self.db)
        normalized_email = validate_user_email(email)
        user = self.user_repo.get_user_by_email(normalized_email)
        if not user:
            return None
        if not logincode_svc.validate_code(user.id, code):
            return None
        self.user_repo.set_user_as_verified(user.id)
        return user