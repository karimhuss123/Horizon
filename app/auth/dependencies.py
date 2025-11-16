from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from core.config import settings
from db.db import get_db
from auth.repositories.user_repo import UserRepo

def require_login(request: Request, db: Session = Depends(get_db)):
    try:
        return get_current_user(request, db)
    except HTTPException as e:
        if e.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_307_TEMPORARY_REDIRECT,
                headers={"Location": "/auth/login"},
            )
        raise

def require_anonymous(request: Request, db = Depends(get_db)):
    try:
        user = get_current_user(request, db)
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/"},
        )
    except HTTPException as e:
        if e.status_code == 401:
            return None
        raise

def get_current_user(request: Request, db: Session = Depends(get_db)):
    header_auth = request.headers.get("Authorization")
    cookie_auth = request.cookies.get("access_token")
    token = None
    if header_auth and header_auth.startswith("Bearer "):
        token = header_auth.split(" ")[1]
    elif cookie_auth and cookie_auth.startswith("Bearer "):
        token = cookie_auth.split(" ")[1]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": True})
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_repo = UserRepo(db)
    user = user_repo.get_user_by_id(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(401, "Not authenticated")
    return user
