from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Secrets and tokens
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Environment and hardening
    ENV: str = "dev"  # dev | prod
    REQUIRE_STRONG_SECRET: bool = True
    HTTPS_REDIRECT: bool = False  # enable in prod behind TLS
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173"

    # Password hashing
    PASSWORD_HASH_ITERATIONS: int = 260_000

    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./app.db"

    # Defaults
    DEFAULT_LAT: float = 31.778  # Jerusalem
    DEFAULT_LON: float = 35.235
    DEFAULT_TZ: str = "Asia/Jerusalem"

    class Config:
        env_file = "backend/.env"

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
