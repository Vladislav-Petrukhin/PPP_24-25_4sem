import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    DATABASE_URL: str = "sqlite:///./app.db"
    CELERY_BROKER_URL: str = "sqla+sqlite:///./celery_broker.db"
    CELERY_RESULT_BACKEND: str = "db+sqlite:///./celery_result.db"

    class Config:
        env_file = ".env"

settings = Settings()
