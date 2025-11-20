import random
import hashlib
from email_validator import validate_email
from core.config import settings
from db.utils.time import current_datetime_et, add_to_datetime
from jose import jwt

def validate_user_email(email):
    emailinfo = validate_email(email, check_deliverability=False)
    return emailinfo.normalized.lower()

def generate_random_code():
    return f"{random.randint(0, 999999):06d}"

def generate_code_hash(code):
    return hashlib.sha256(code.encode()).hexdigest()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = current_datetime_et()
    expire = add_to_datetime(dt=now, days=settings.ACCESS_TOKEN_EXPIRY_DAYS)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)