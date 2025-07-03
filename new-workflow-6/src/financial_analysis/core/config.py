# File: src/financial_analysis/core/config.py
# Purpose: Centralized application configuration. (Updated for Redis)

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Holds all application settings, now powered by pydantic-settings
    to automatically read from environment variables or a .env file.
    """
    # Project Info
    PROJECT_NAME: str = "Automated Financial Analysis System"

    # Directory Setup
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    REPORTS_DIR: Path = BASE_DIR / "reports"
    LOGS_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOGS_DIR / "financial_analysis.log"

    # SEC EDGAR API Configuration (loaded from .env)
    SEC_USER_AGENT: str = "Default Agent default@example.com"
    
    # Data Request Settings
    REQUEST_DELAY_SECONDS: float = 0.2
    NUM_HISTORICAL_YEARS: int = 5

    # Redis Cache Configuration (loaded from .env)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_EXPIRATION_SECONDS: int = 86400 # 24 hours

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

# Instantiate the settings object for easy import across the application
settings = Settings()
