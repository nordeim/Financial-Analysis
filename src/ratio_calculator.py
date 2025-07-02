# File: src/ratio_calculator.py
from utils.logger import get_logger

logger = get_logger(__name__)

class RatioCalculator:
    def calculate_all_ratios(self, fin_data, market_data):
        # Compute ratios from standardized dataframes in fin_data dict
        ratios = {}
        try:
            # Example: Current Ratio
            if "CurrentAssets" in fin_data and "CurrentLiabilities" in fin_data:
                ca = fin_data["CurrentAssets"].iloc[0]["value"]
                cl = fin_data["CurrentLiabilities"].iloc[0]["value"]
                ratios["Current Ratio"] = ca / cl if cl else None

            # Example: Net Profit Margin
            if "NetIncome" in fin_data and "Revenue" in fin_data:
                ni = fin_data["NetIncome"].iloc[0]["value"]
                rev = fin_data["Revenue"].iloc[0]["value"]
                ratios["Net Profit Margin"] = ni / rev if rev else None

            # Example: Debt-to-Equity
            if "TotalLiabilities" in fin_data and "StockholdersEquity" in fin_data:
                debt = fin_data["TotalLiabilities"].iloc[0]["value"]
                eq = fin_data["StockholdersEquity"].iloc[0]["value"]
                ratios["Debt-to-Equity"] = debt / eq if eq else None

            # ... additional ratios ...
            logger.info("Ratios calculated successfully")
        except Exception as e:
            logger.warning(f"Error calculating ratios: {e}")
        return ratios
