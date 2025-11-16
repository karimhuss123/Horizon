import random
import hashlib
from email_validator import validate_email, EmailNotValidError
from core.config import settings
from db.utils.time import current_datetime_utc, add_to_datetime
from jose import jwt
from typing import List, Optional
from fastapi_mail import FastMail, MessageSchema, MessageType
from core.config import mail_config

def validate_user_email(email):
    emailinfo = validate_email(email, check_deliverability=False)
    return emailinfo.normalized.lower()

def generate_random_code():
    return f"{random.randint(0, 999999):06d}"

def generate_code_hash(code):
    return hashlib.sha256(code.encode()).hexdigest()

async def send_login_code_email(code, email):
    html = f"""
    <html>
      <body>
        <h2>Your Login Code</h2>
        <p style="font-size: 18px;">Code: <strong>{code}</strong></p>
      </body>
    </html>
    """
    await send_mail(
        recipients=[email],
        subject="Your Login Code",
        body=html,
    )

async def send_mail(
    recipients: List[str],
    subject: str,
    body: str,
    html: bool = True,
    attachments: Optional[List[str]] = [],
):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html if html else MessageType.plain,
        attachments=attachments,
    )
    fm = FastMail(mail_config)
    await fm.send_message(message)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    now = current_datetime_utc()
    expire = add_to_datetime(dt=now, minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)