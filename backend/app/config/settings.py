"""
Application settings and configuration.

This file manages all configuration from environment variables.
Follows 12-factor app methodology.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ============ APP CONFIGURATION ============
    APP_NAME: str = "CloudOps Intelligence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ============ DATABASE CONFIGURATION ============
    DATABASE_URL: str = "postgresql://cloudops:cloudops123@localhost:5432/cloudops_db"
    SQLALCHEMY_ECHO: bool = False
    
    # ============ SERVER CONFIGURATION ============
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # ============ SECURITY CONFIGURATION ============
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ============ AI/LLM CONFIGURATION ============
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_MAX_TOKENS: int = 1000
    AI_ENABLED: bool = True
    
    # ============ MONITORING CONFIGURATION ============
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    # ============ LOGGING CONFIGURATION ============
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # ============ EXTERNAL SERVICES ============
    SLACK_WEBHOOK_URL: Optional[str] = None
    PAGERDUTY_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra fields from environment
        extra = "allow"


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings.
    
    Dependency injection helper for FastAPI.
    """
    return settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Settings loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
