# File: src/financial_analysis/data_providers/sec_edgar_provider.py
# Purpose: Implements the data provider for SEC EDGAR, now with Redis caching. (Updated)

import requests
import logging
import json
import redis
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from ..core.models import (
    CompanyInfo, FinancialStatement, IncomeStatement, BalanceSheet, CashFlowStatement
)
from .base_provider import BaseDataProvider, DataProviderError
from ..core.config import settings

logger = logging.getLogger(__name__)

# MODIFIED: Expanded the tag map with more common aliases to improve parsing robustness.
XBRL_TAG_MAP = {
    # Income Statement
    "revenue": ["Revenues", "SalesRevenueNet", "TotalRevenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "cost_of_goods_sold": ["CostOfGoodsAndServicesSold", "CostOfRevenue"],
    "gross_profit": ["GrossProfit"],
    "operating_income": ["OperatingIncomeLoss"],
    "interest_expense": ["InterestExpense"],
    "net_income": ["NetIncomeLoss", "ProfitLoss"],
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
    "total_debt": ["DebtCurrent", "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations", "LongTermDebtNoncurrent"],
    "shareholders_equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "shares_outstanding": ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"],
    # Cash Flow Statement
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_expenditures": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "dividend_payments": ["PaymentsOfDividends"],
}


class SecEdgarProvider(BaseDataProvider):
    """Provides financial data by fetching it from the SEC EDGAR API, with Redis caching."""
    
    BASE_URL = "https://data.sec.gov"
    CIK_MAP_URL = "https://www.sec.gov/files/company_tickers.json"

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": settings.SEC_USER_AGENT})
        self._cik_map = None
        
        try:
            self._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True
            )
            self._redis_client.ping()
            logger.info("Successfully connected to Redis cache.")
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Could not connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}. Caching will be disabled. Error: {e}")
            self._redis_client = None

    def _get_with_cache(self, cache_key: str, url: str) -> Dict[str, Any]:
        """Generic getter that checks cache first, then falls back to HTTP GET."""
        if self._redis_client:
            cached_data = self._redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for key: {cache_key}")
                return json.loads(cached_data)
        
        logger.info(f"Cache MISS for key: {cache_key}. Fetching from URL: {url}")
        try:
            response = self._session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if self._redis_client:
                self._redis_client.setex(
                    cache_key,
                    settings.REDIS_CACHE_EXPIRATION_SECONDS,
                    json.dumps(data)
                )
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed for URL {url}: {e}")
            raise DataProviderError(f"Network request failed for {url}: {e}")

    def _load_cik_map(self) -> Dict[str, Any]:
        if self._cik_map:
            return self._cik_map
        
        cache_key = "sec:cik_map"
        data = self._get_with_cache(cache_key, self.CIK_MAP_URL)
        
        self._cik_map = {company['ticker']: company for company in data.values()}
        logger.info(f"Successfully loaded CIK map for {len(self._cik_map)} tickers.")
        return self._cik_map

    def _get_company_facts(self, cik: str) -> Dict[str, Any]:
        cache_key = f"sec:facts:{cik}"
        facts_url = f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        return self._get_with_cache(cache_key, facts_url)

    def _get_cik(self, ticker: str) -> str:
        ticker = ticker.upper()
        cik_map = self._load_cik_map()
        if ticker not in cik_map:
            raise DataProviderError(f"Ticker '{ticker}' not found in SEC CIK mapping.")
        cik_str = str(cik_map[ticker]['cik_str'])
        return cik_str.zfill(10)

    def get_company_info(self, ticker: str) -> CompanyInfo:
        logger.info(f"Getting company info for {ticker} from SEC provider.")
        cik_map = self._load_cik_map()
        ticker_upper = ticker.upper()
        if ticker_upper not in cik_map:
            raise DataProviderError(f"Ticker '{ticker_upper}' not found in SEC CIK mapping.")
        company_data = cik_map[ticker_upper]
        return CompanyInfo(ticker=ticker_upper, name=company_data.get('title', 'N/A'), cik=str(company_data.get('cik_str')).zfill(10), exchange=company_data.get('exchange', 'N/A'))

    def get_financial_statements(self, ticker: str, num_years: int) -> List[FinancialStatement]:
        logger.info(f"Getting financial statements for {ticker} from SEC provider.")
        cik = self._get_cik(ticker)
        facts = self._get_company_facts(cik)
        if "facts" not in facts or "us-gaap" not in facts["facts"]:
            raise DataProviderError(f"No US-GAAP facts found for CIK {cik}.")
        gaap_facts = facts["facts"]["us-gaap"]
        
        def get_fact_data(metric_key: str) -> List[Dict]:
            """Finds all matching tags and returns their data lists."""
            all_items = []
            for tag in XBRL_TAG_MAP.get(metric_key, []):
                if tag in gaap_facts and "units" in gaap_facts[tag] and "USD" in gaap_facts[tag]["units"]:
                    all_items.extend(gaap_facts[tag]["units"]["USD"])
            return all_items

        annual_data = defaultdict(lambda: defaultdict(dict))
        
        # Aggregate data from all possible tags
        aggregated_facts = defaultdict(list)
        for metric in XBRL_TAG_MAP:
            aggregated_facts[metric] = get_fact_data(metric)
            
        # Group by fiscal year
        for metric, items in aggregated_facts.items():
            for item in items:
                if item.get("form") == "10-K" and item.get("fp") == "FY":
                    fy = item["fy"]
                    # Sum values if multiple tags contribute to one metric (e.g., total_debt)
                    annual_data[fy][metric] = annual_data[fy].get(metric, 0) + item["val"]
                    if "end_date" not in annual_data[fy]:
                         annual_data[fy]["end_date"] = datetime.strptime(item["end"], "%Y-%m-%d")

        statements = []
        sorted_years = sorted(annual_data.keys(), reverse=True)
        
        for year in sorted_years[:num_years]:
            data = annual_data[year]
            if "end_date" not in data: continue # Skip years with incomplete data
            
            def d(key): return data.get(key)
            
            income_stmt = IncomeStatement(revenue=d("revenue"), cost_of_goods_sold=d("cost_of_goods_sold"), gross_profit=d("gross_profit"), operating_income=d("operating_income"), interest_expense=d("interest_expense"), net_income=d("net_income"), eps_diluted=d("eps_diluted"), eps_basic=d("eps_basic"))
            balance_sheet = BalanceSheet(total_assets=d("total_assets"), current_assets=d("current_assets"), cash_and_equivalents=d("cash_and_equivalents"), inventory=d("inventory"), accounts_receivable=d("accounts_receivable"), total_liabilities=d("total_liabilities"), current_liabilities=d("current_liabilities"), total_debt=d("total_debt"), shareholders_equity=d("shareholders_equity"), shares_outstanding=d("shares_outstanding"))
            cash_flow_stmt = CashFlowStatement(operating_cash_flow=d("operating_cash_flow"), capital_expenditures=d("capital_expenditures"), dividend_payments=d("dividend_payments"))
            
            statements.append(FinancialStatement(ticker=ticker.upper(), period="FY", fiscal_year=year, end_date=data["end_date"], income_statement=income_stmt, balance_sheet=balance_sheet, cash_flow_statement=cash_flow_stmt, source_url=f"{self.BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"))
            
        if not statements:
            raise DataProviderError(f"Could not construct any financial statements for {ticker}. The company might not file 10-Ks or data is unavailable.")
        
        return statements
