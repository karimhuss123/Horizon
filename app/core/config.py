from pydantic_settings import BaseSettings

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
