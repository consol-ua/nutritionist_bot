from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional, Dict


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str
    WEBHOOK_URL: str

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    PROJECT_ID: str

    # FastAPI
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Environment
    ENVIRONMENT: str = "development"

    # Ngrok
    NGROK_AUTH_TOKEN: Optional[str] = None

    # Content
    START_VIDEO_FILE_ID:str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def get_google_credentials(self) -> Optional[Dict[str, str]]:
        if self.is_production():
            # В продакшені використовуємо Workload Identity
            return None
        elif self.GOOGLE_APPLICATION_CREDENTIALS:
            # В розробці використовуємо файл з обліковими даними
            return {"credentials_file": self.GOOGLE_APPLICATION_CREDENTIALS}
        return None


def get_settings() -> Settings:
    settings = Settings()
    print(f"Loaded WEBHOOK_URL: {settings.WEBHOOK_URL}")
    return settings