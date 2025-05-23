from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    REDIS_BROKER_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
