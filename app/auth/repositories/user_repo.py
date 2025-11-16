from sqlalchemy.orm import Session
from db.models import User

class UserRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, email):
        user = self.get_user_by_email(email)
        if not user:
            user = User(email=email)
            self.db.add(user)
            self.db.commit()
        return user
    
    def get_user_by_email(self, email):
        return self.db.query(User).filter_by(email=email).first()
    
    def get_user_by_id(self, id):
        return self.db.query(User).filter_by(id=id).first()
    
    def set_user_as_verified(self, user_id):
        (
            self.db.query(User)
            .filter(User.id == user_id)
            .update(
                {
                    User.is_verified: True
                },
                synchronize_session=False
            )
        )
        self.db.commit()