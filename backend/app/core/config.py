from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"
    DEFAULT_LAT: float = 31.778  # Jerusalem
    DEFAULT_LON: float = 35.235
    DEFAULT_TZ: str = "Asia/Jerusalem"

    class Config:
        env_file = "backend/.env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
