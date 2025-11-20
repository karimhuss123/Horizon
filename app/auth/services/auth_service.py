from sqlalchemy.orm import Session
from auth.utils.auth_utils import validate_user_email
from auth.repositories.user_repo import UserRepo
from auth.services.logincode_service import LoginCodeService
from clients.resend_client import ResendClient

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepo(db)
        self.email_client = ResendClient()
    
    def process_code_request(self, email, background_tasks):
        logincode_svc = LoginCodeService(self.db)
        normalized_email = validate_user_email(email)
        user = self.users.get_or_create_user(normalized_email)
        code = logincode_svc.generate_code(user.id)
        background_tasks.add_task(self.email_client.send_login_code, code, user.email)
    
    def verify_code(self, email, code):
        logincode_svc = LoginCodeService(self.db)
        normalized_email = validate_user_email(email)
        user = self.users.get_user_by_email(normalized_email)
        if not user:
            return None
        if not logincode_svc.validate_code(user.id, code):
            return None
        self.users.set_user_as_verified(user.id)
        return user
    
    def delete_user(self, id):
        self.users.delete(id)
