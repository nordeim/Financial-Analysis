# File: src/financial_analysis/data_providers/sec_edgar_provider.py
# Purpose: Implements the data provider for fetching data from the SEC EDGAR database.

import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from ..core.models import (
    CompanyInfo, FinancialStatement, IncomeStatement, BalanceSheet, CashFlowStatement
)
from .base_provider import BaseDataProvider, DataProviderError
from ..core.config import settings

logger = logging.getLogger(__name__)

# Mapping from our model fields to a list of potential US-GAAP XBRL tags.
# The list is ordered by preference.
XBRL_TAG_MAP = {
    # Income Statement
    "revenue": ["Revenues", "SalesRevenueNet", "TotalRevenues"],
    "cost_of_goods_sold": ["CostOfGoodsAndServicesSold", "CostOfRevenue"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "interest_expense": ["InterestExpense"],
    "net_income": ["NetIncomeLoss"],
    "eps_diluted": ["EarningsPerShareDiluted"],
    "eps_basic": ["EarningsPerShareBasic"],
    # Balance Sheet
    "cash_and_equivalents": ["CashAndCashEquivalentsAtCarryingValue"],
    "accounts_receivable": ["AccountsReceivableNetCurrent"],
    "inventory": ["InventoryNet"],
    "current_assets": ["AssetsCurrent"],
    "total_assets": ["Assets"],
    "current_liabilities": ["LiabilitiesCurrent"],
    "total_liabilities": ["Liabilities"],
    "total_debt": ["LongTermDebtAndCapitalLeaseObligations", "DebtCurrent"], # Needs summation
    "shareholders_equity": ["StockholdersEquity"],
    "shares_outstanding": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"],
    # Cash Flow Statement
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditures": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "dividend_payments": ["PaymentsOfDividends"],
}

class SecEdgarProvider(BaseDataProvider):
    """Provides financial data by fetching it from the SEC EDGAR API."""
    
    BASE_URL = "https://data.sec.gov"
    CIK_MAP_URL = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": settings.SEC_USER_AGENT})
        self._cik_map = None
        self._company_facts_cache = {} # Simple in-memory cache for company facts

    def _load_cik_map(self) -> Dict[str, Any]:
        """Loads the Ticker-to-CIK mapping from the SEC. Caches it in memory."""
        if self._cik_map:
            return self._cik_map
        
        logger.info("Downloading SEC Ticker-to-CIK mapping file...")
        try:
            response = self._session.get(self.CIK_MAP_URL)
            response.raise_for_status()
            # The JSON file has integer keys, so we just use the values.
            # We create a map from Ticker -> CIK details.
            all_companies = response.json()
            self._cik_map = {company['ticker']: company for company in all_companies.values()}
            logger.info(f"Successfully loaded CIK map for {len(self._cik_map)} tickers.")
            return self._cik_map
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download CIK map: {e}")
            raise DataProviderError(f"Could not retrieve CIK mapping from SEC: {e}")

    def _get_cik(self, ticker: str) -> str:
        """Gets the CIK for a given ticker, padding with zeros."""
        ticker = ticker.upper()
        cik_map = self._load_cik_map()
        if ticker not in cik_map:
            raise DataProviderError(f"Ticker '{ticker}' not found in SEC CIK mapping.")
        
        cik_str = str(cik_map[ticker]['cik_str'])
        return cik_str.zfill(10) # CIK must be 10 digits

    def _get_company_facts(self, cik: str) -> Dict[str, Any]:
        """Fetches all company facts for a given CIK from the SEC API."""
        if cik in self._company_facts_cache:
            return self._company_facts_cache[cik]
            
        facts_url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        logger.info(f"Fetching company facts for CIK {cik} from {facts_url}")
        try:
            response = self._session.get(facts_url)
            response.raise_for_status()
            facts = response.json()
            self._company_facts_cache[cik] = facts
            return facts
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch company facts for CIK {cik}: {e}")
            raise DataProviderError(f"Could not retrieve company facts for CIK {cik}: {e}")

    def get_company_info(self, ticker: str) -> CompanyInfo:
        logger.info(f"Getting company info for {ticker} from SEC provider.")
        cik_map = self._load_cik_map()
        ticker_upper = ticker.upper()
        
        if ticker_upper not in cik_map:
            raise DataProviderError(f"Ticker '{ticker_upper}' not found in SEC CIK mapping.")
            
        company_data = cik_map[ticker_upper]
        return CompanyInfo(
            ticker=ticker_upper,
            name=company_data.get('title', 'N/A'),
            cik=str(company_data.get('cik_str')).zfill(10),
            exchange=company_data.get('exchange', 'N/A')
        )

    def get_financial_statements(self, ticker: str, num_years: int) -> List[FinancialStatement]:
        logger.info(f"Getting financial statements for {ticker} from SEC provider.")
        cik = self._get_cik(ticker)
        facts = self._get_company_facts(cik)
        
        if "facts" not in facts or "us-gaap" not in facts["facts"]:
            raise DataProviderError(f"No US-GAAP facts found for CIK {cik}.")
            
        gaap_facts = facts["facts"]["us-gaap"]
        
        # This helper function will find the first available tag for a given metric
        def get_fact_data(metric_key: str) -> Optional[Dict]:
            for tag in XBRL_TAG_MAP.get(metric_key, []):
                if tag in gaap_facts:
                    return gaap_facts[tag]
            return None

        # Structure to hold data pivoted by fiscal year and period
        # defaultdict(lambda: defaultdict(dict)) is a nested dictionary
        annual_data = defaultdict(lambda: defaultdict(dict))

        for metric, tags in XBRL_TAG_MAP.items():
            fact_data = get_fact_data(metric)
            if not fact_data or "units" not in fact_data:
                continue

            # Assuming USD for simplicity, could be extended for other currencies
            if "USD" in fact_data["units"]:
                for item in fact_data["units"]["USD"]:
                    # We are only interested in annual data (10-K filings)
                    # These have a form '10-K' and an approximate 365 day frame
                    if item.get("form") == "10-K" and item.get("fp") == "FY":
                        fy = item["fy"]
                        end_date = datetime.strptime(item["end"], "%Y-%m-%d")
                        annual_data[fy][metric] = item["val"]
                        annual_data[fy]["end_date"] = end_date
        
        # Now, construct the FinancialStatement objects
        statements = []
        # Sort years descending to get most recent first
        sorted_years = sorted(annual_data.keys(), reverse=True)

        for year in sorted_years[:num_years]:
            data = annual_data[year]
            
            # Helper to get value or None
            def d(key): return data.get(key)
            
            # Special handling for debt
            total_debt_val = (d("total_debt") or 0) + (d("debt_current_from_tag") or 0)
            
            income_stmt = IncomeStatement(
                revenue=d("revenue"),
                cost_of_goods_sold=d("cost_of_goods_sold"),
                gross_profit=d("gross_profit"),
                operating_income=d("operating_income"),
                interest_expense=d("interest_expense"),
                net_income=d("net_income"),
                eps_diluted=d("eps_diluted"),
                eps_basic=d("eps_basic"),
            )
            balance_sheet = BalanceSheet(
                total_assets=d("total_assets"),
                current_assets=d("current_assets"),
                cash_and_equivalents=d("cash_and_equivalents"),
                inventory=d("inventory"),
                accounts_receivable=d("accounts_receivable"),
                total_liabilities=d("total_liabilities"),
                current_liabilities=d("current_liabilities"),
                total_debt=total_debt_val if total_debt_val > 0 else None,
                shareholders_equity=d("shareholders_equity"),
                shares_outstanding=d("shares_outstanding"),
            )
            cash_flow_stmt = CashFlowStatement(
                operating_cash_flow=d("operating_cash_flow"),
                capital_expenditures=d("capital_expenditures"),
                dividend_payments=d("dividend_payments"),
            )
            
            statements.append(
                FinancialStatement(
                    ticker=ticker.upper(),
                    period="FY",
                    fiscal_year=year,
                    end_date=data["end_date"],
                    income_statement=income_stmt,
                    balance_sheet=balance_sheet,
                    cash_flow_statement=cash_flow_stmt,
                    source_url=f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
                )
            )

        if not statements:
            raise DataProviderError(f"Could not construct any financial statements for {ticker}. The company might not file 10-Ks or data is unavailable.")
            
        return statements
