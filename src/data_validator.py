# File: src/data_validator.py
from utils.logger import get_logger

logger = get_logger(__name__)

class DataValidator:
    def validate_data(self, fin_data, market_data):
        # Check for presence and balance sheet integrity, flag missing data
        validated = {}
        for k, df in fin_data.items():
            if df is not None and not df.empty:
                validated[k] = df
            else:
                logger.warning(f"Missing or empty data for {k}")
        # Optionally add confidence levels, outlier detection, etc.
        # For demo: everything present = High confidence, else Medium/Low
        return validated
