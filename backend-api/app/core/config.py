import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App configuration
    APP_NAME: str = "SEN TRAFIC AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database configuration
    DATABASE_URL: str = "postgresql://sentrafic:sentrafic_dev@localhost:5432/sentrafic"

    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT configuration
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    # Default admin credentials
    ADMIN_EMAIL: str = "admin@sentrafic.sn"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
