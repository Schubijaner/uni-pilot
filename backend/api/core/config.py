"""Application configuration settings."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///uni_pilot.db"

    # AWS Bedrock Configuration
    # Default region: us-east-1 (matches sample script)
    # Can be overridden via AWS_REGION environment variable or aws configure
    AWS_REGION: str = "us-east-1"
    # Optional: Only set if not using aws configure or IAM roles
    # If None, boto3 will use standard credential chain (aws configure, IAM role, etc.)
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    BEDROCK_MODEL_CHAT: str = "anthropic.claude-3-haiku-20240307-v1:0"
    BEDROCK_MODEL_ROADMAP: str = "anthropic.claude-3-sonnet-20240229-v1:0"

    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"  # Should be set via env var
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]  # In production, specify exact origins

    # LLM Settings
    MAX_CHAT_HISTORY_MESSAGES: int = 20
    CHAT_TEMPERATURE: float = 0.7
    ROADMAP_TEMPERATURE: float = 0.3  # Less creative for structured data

    # Logging
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

