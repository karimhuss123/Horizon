from pydantic_settings import BaseSettings
from pydantic import EmailStr
from fastapi_mail import ConnectionConfig
import os

class Settings(BaseSettings):
    APP_NAME: str | None = None
    DATABASE_URL: str | None = None

    OPENAI_KEY: str | None = None
    OPENAI_CHAT_MODEL: str | None = None
    OPENAI_EMBEDDINGS_MODEL: str | None = None
    INTENT_TEMP: float = 0.0
    REGEN_TEMP: float = 0.1
    RATIONALE_TEMP: float = 0.25
    BASKET_SUGGESTION_TEMP: float = 0.25
    
    MAX_HOLDINGS_COUNT: int = 25
    DEFAULT_HOLDINGS_COUNT: int = 10
    AI_SUGGESTIONS_COUNT: int = 5
    
    RESEND_API_KEY: str | None = None
    RESEND_NO_REPLY_DEFAULT_SENDER: str | None = None
    
    LOGIN_CODE_VERIFICATION_MAX_ATTEMPTS: int = 5
    LOGIN_CODE_MINUTES_TO_EXPIRY: int = 10
    SECRET_KEY: str | None = None
    JWT_ALGORITHM: str | None = None
    ACCESS_TOKEN_EXPIRY_DAYS: int = 5
    
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    SSL_CERT_FILE: str

    @property
    def TEMPERATURES(self) -> dict:
        return {
            "intent": self.INTENT_TEMP,
            "regeneration": self.REGEN_TEMP,
            "rationale": self.RATIONALE_TEMP,
            "basket_suggestion": self.BASKET_SUGGESTION_TEMP
        }
    
    class Config:
        env_file = ".env"

settings = Settings()

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

os.environ["SSL_CERT_FILE"] = settings.SSL_CERT_FILE