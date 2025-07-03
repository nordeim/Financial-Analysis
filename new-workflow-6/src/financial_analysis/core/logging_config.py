# File: src/financial_analysis/core/logging_config.py
# Purpose: Provides a centralized, dictionary-based logging configuration.

import logging.config
from .config import settings

def setup_logging():
    """
    Configures logging for the entire application using a dictionary configuration.
    This setup provides two handlers: one for console output and one for file output.
    """
    # Ensure logs directory exists
    settings.LOGS_DIR.mkdir(exist_ok=True)

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filename': settings.LOG_FILE,
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'encoding': 'utf-8',
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            },
            'httpx': { # Quieter logging for http libraries
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False,
            },
            'httpcore': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False,
            },
             'yfinance': {
                'handlers': ['console', 'file'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
