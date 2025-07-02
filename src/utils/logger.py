# File: src/utils/logger.py
import logging
import sys
from pathlib import Path

def setup_logging(level="INFO", log_file=None):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers.clear()
    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)
    # File
    fh = logging.FileHandler(log_dir / "financial_analyzer.log")
    fh.setFormatter(formatter)
    root.addHandler(fh)

def get_logger(name):
    return logging.getLogger(name)
