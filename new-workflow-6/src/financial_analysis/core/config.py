# File: src/financial_analysis/core/config.py
# Purpose: Centralized application configuration.

from pathlib import Path

class Settings:
    """
    Holds all application settings.
    Using a class provides a namespace and makes settings easy to import.
    """
    # Project Info
    PROJECT_NAME: str = "Automated Financial Analysis System"

    # Directory Setup
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    REPORTS_DIR: Path = BASE_DIR / "reports"
    LOGS_DIR: Path = BASE_DIR / "logs"
    LOG_FILE: Path = LOGS_DIR / "financial_analysis.log"

    # SEC EDGAR API Configuration
    # IMPORTANT: The SEC requires a custom User-Agent of the form 'Company Name contact@example.com'
    # This helps them identify the source of traffic.
    SEC_USER_AGENT: str = "My Educational Project my-email@example.com"
    
    # Data Request Settings
    REQUEST_DELAY_SECONDS: float = 0.2  # Delay between requests to avoid overwhelming servers (SEC allows up to 10/sec)
    NUM_HISTORICAL_YEARS: int = 5 # Default number of years of data to fetch

# Instantiate the settings object for easy import across the application
settings = Settings()
