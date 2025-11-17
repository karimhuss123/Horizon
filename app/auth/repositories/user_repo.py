from sqlalchemy.orm import Session
from db.models import User
from fastapi import HTTPException

class UserRepo:
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_user(self, email):
        # Not using get helper function to not raise error if user is not found and needs to be created
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            self.db.add(user)
            self.db.commit()
        return user
    
    def get_user_by_email(self, email):
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    def get_user_by_id(self, id):
        user = self.db.query(User).filter_by(id=id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
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
    
    def delete(self, user_id):
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        self.db.delete(user)
        self.db.commit()
        return True