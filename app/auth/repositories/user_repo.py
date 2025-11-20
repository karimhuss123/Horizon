from sqlalchemy.orm import Session
from db.models import User
from fastapi import HTTPException
from db.utils.time import current_datetime_et
from core.errors.messages import messages
from investment_engine.repositories.basket_repo import BasketRepo

class UserRepo:
    def __init__(self, db: Session):
        self.db = db
        self.baskets = BasketRepo(db)
    
    def get_or_create_user(self, email):
        # Not using get helper function to not raise error if user is not found and needs to be created
        user = self.db.query(User).filter_by(email=email).first()
        if not user:
            user = User(email=email)
            self.db.add(user)
        elif user.deleted_at is not None:
            user.deleted_at = None
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email):
        user = (
            self.db.query(User)
            .filter(User.email==email, User.deleted_at.is_(None))
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail=messages.user_not_found)
        return user
    
    def get_user_by_id(self, id):
        user = (
            self.db.query(User)
            .filter(User.id==id, User.deleted_at.is_(None))
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail=messages.user_not_found)
        return user
    
    def set_user_as_verified(self, user_id):
        user = self.get_user_by_id(user_id)
        user.is_verified = True
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user_id):
        user = self.get_user_by_id(user_id)
        user.deleted_at = current_datetime_et()
        deleted_baskets = self.baskets.delete_all_baskets_for_user(user.id)
        self.db.commit()
        return True