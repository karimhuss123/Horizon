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
    
    LOGIN_CODE_DAILY_LIMIT: int = 10
    BASKET_GENERATION_DAILY_LIMIT: int = 10
    BASKET_REGENERATION_DAILY_LIMIT: int = 20
    
    REDIS_URL: str
    
    # --- Rate limits ---
    RATE_LIMIT_AUTH_CODE_REQUEST: str = "5/minute;60/hour"
    RATE_LIMIT_AUTH_CODE_VERIFY: str = "20/minute;100/hour"
    
    RATE_LIMIT_BASKETS_GENERATE: str = "5/minute;15/hour"
    RATE_LIMIT_BASKETS_REGENERATE: str = "6/minute;30/hour"
    RATE_LIMIT_BASKETS_EDIT: str = "5/minute;40/hour;120/day"
    RATE_LIMIT_BASKETS_GENERATE_SUGGESTIONS: str = "10/minute;15/hour;30/day"
    
    CHART_INITIAL_VALUE: int = 100

    @property
    def TEMPERATURES(self) -> dict:
        return {
            "intent": self.INTENT_TEMP,
            "regeneration": self.REGEN_TEMP,
            "rationale": self.RATIONALE_TEMP,
            "basket_suggestion": self.BASKET_SUGGESTION_TEMP
        }
    
    CELERY_TASK_FILES : list = [
        "app.tasks.basket_tasks"
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()