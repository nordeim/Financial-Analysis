# File: src/data_extractor.py
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

class DataExtractor:
    async def extract_all_statements(self, filings, years=5):
        """
        Extract key financial items from SEC XBRL filings.
        Returns standardized dict of Income, Balance Sheet, Cash Flow.
        """
        if not filings or "facts" not in filings:
            logger.warning("No filings to extract, returning empty dict.")
            return {}
        us_gaap = filings["facts"].get("us-gaap", {})
        # Key line items mapping
        key_items = {
            'Revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
            'NetIncome': ['NetIncomeLoss'],
            'TotalAssets': ['Assets'],
            'TotalLiabilities': ['Liabilities'],
            'StockholdersEquity': ['StockholdersEquity'],
            'OperatingIncome': ['OperatingIncomeLoss'],
            'CostOfRevenue': ['CostOfRevenue'],
            'CurrentAssets': ['AssetsCurrent'],
            'CurrentLiabilities': ['LiabilitiesCurrent'],
            'Cash': ['CashAndCashEquivalentsAtCarryingValue'],
            'OperatingCashFlow': ['NetCashProvidedByUsedInOperatingActivities']
        }
        statements = {}
        for std_name, sec_keys in key_items.items():
            found = None
            for k in sec_keys:
                if k in us_gaap:
                    found = us_gaap[k]
                    break
            if found:
                data = []
                for unit, vals in found.get("units", {}).items():
                    for v in vals:
                        if v.get("form") == "10-K" and 'fy' in v:
                            data.append({
                                "fiscal_year": v["fy"],
                                "end_date": v["end"],
                                "value": v["val"],
                                "unit": unit
                            })
                if data:
                    df = pd.DataFrame(data)
                    df = df.sort_values('end_date', ascending=False).head(years)
                    statements[std_name] = df
                    logger.info(f"Extracted {std_name}: {len(df)} years")
        return statements
