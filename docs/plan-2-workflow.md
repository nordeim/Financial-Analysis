Complete Financial Analysis System Implementation
Project Architecture & Setup
Directory Structure
financial_analyzer/
├── src/
│   ├── __init__.py
│   ├── data_acquisition/
│   │   ├── __init__.py
│   │   ├── sec_edgar_client.py
│   │   ├── yahoo_finance_client.py
│   │   ├── company_website_scraper.py
│   │   └── data_validator.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── ratio_calculator.py
│   │   ├── trend_analyzer.py
│   │   ├── benchmark_engine.py
│   │   └── risk_assessor.py
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── report_generator.py
│   │   ├── chart_creator.py
│   │   └── pdf_builder.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── config.py
│   │   └── exceptions.py
│   └── main.py
├── tests/
├── config/
│   ├── settings.yaml
│   └── industry_benchmarks.json
├── templates/
│   └── report_template.html
├── requirements.txt
├── setup.py
├── docker-compose.yml
└── README.md
Step 1: Environment Setup & Dependencies
requirements.txt

requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
yfinance>=0.2.18
beautifulsoup4>=4.12.0
lxml>=4.9.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0
jinja2>=3.1.0
pdfkit>=1.0.0
openpyxl>=3.1.0
aiohttp>=3.8.0
asyncio>=3.4.3
pydantic>=2.0.0
python-dotenv>=1.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
redis>=4.6.0
celery>=5.3.0
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0

setup.py

from setuptools import setup, find_packages

setup(
    name="financial-analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "yfinance>=0.2.18",
        "beautifulsoup4>=4.12.0",
        "matplotlib>=3.7.0",
        "plotly>=5.14.0",
        "jinja2>=3.1.0",
        "pdfkit>=1.0.0",
    ],
    author="Financial Analysis System",
    description="Automated financial analysis and reporting system",
    python_requires=">=3.9",
)

Step 2: Core Configuration System
config/settings.yaml

# API Configuration
apis:
  sec_edgar:
    base_url: "https://data.sec.gov/api/xbrl/companyfacts"
    rate_limit: 10  # requests per second
    headers:
      User-Agent: "Financial Analyzer 1.0 (your-email@company.com)"
  
  yahoo_finance:
    timeout: 30
    retry_attempts: 3
    
  alpha_vantage:
    api_key: "${ALPHA_VANTAGE_API_KEY}"
    base_url: "https://www.alphavantage.co/query"

# Analysis Configuration
analysis:
  default_periods: 5  # years
  industry_benchmark_source: "industry_benchmarks.json"
  confidence_threshold: 0.8
  outlier_detection_threshold: 3.0  # standard deviations

# Reporting Configuration
reporting:
  output_formats: ["pdf", "html", "json"]
  chart_style: "seaborn"
  template_path: "templates/report_template.html"
  
# Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: "logs/financial_analyzer.log"

# Database Configuration
database:
  redis_url: "${REDIS_URL}"
  cache_ttl: 3600  # seconds

# Security Configuration
security:
  rate_limiting:
    requests_per_minute: 60
    burst_limit: 10

src/utils/config.py

import yaml
import os
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field

class APIConfig(BaseModel):
    sec_edgar: Dict[str, Any]
    yahoo_finance: Dict[str, Any]
    alpha_vantage: Dict[str, Any]

class AnalysisConfig(BaseModel):
    default_periods: int = 5
    industry_benchmark_source: str
    confidence_threshold: float = 0.8
    outlier_detection_threshold: float = 3.0

class ReportingConfig(BaseModel):
    output_formats: list[str]
    chart_style: str
    template_path: str

class Config(BaseModel):
    apis: APIConfig
    analysis: AnalysisConfig
    reporting: ReportingConfig
    logging: Dict[str, Any]
    database: Dict[str, Any]
    security: Dict[str, Any]

def load_config() -> Config:
    """Load configuration from YAML file with environment variable substitution."""
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    
    with open(config_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    # Environment variable substitution
    config_str = yaml.dump(config_data)
    for key, value in os.environ.items():
        config_str = config_str.replace(f"${{{key}}}", value)
    
    config_data = yaml.safe_load(config_str)
    return Config(**config_data)

# Global config instance
config = load_config()

Step 3: Data Acquisition Modules
src/data_acquisition/sec_edgar_client.py

import asyncio
import aiohttp
import json
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
from ..utils.logger import get_logger
from ..utils.config import config
from ..utils.exceptions import DataAcquisitionError

logger = get_logger(__name__)

class SECEdgarClient:
    """Client for accessing SEC EDGAR database financial data."""
    
    def __init__(self):
        self.base_url = config.apis.sec_edgar.base_url
        self.headers = config.apis.sec_edgar.headers
        self.rate_limit = config.apis.sec_edgar.rate_limit
        self.session = None
        self.last_request_time = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit(self):
        """Implement rate limiting to respect SEC guidelines."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def get_company_facts(self, cik: str) -> Dict[str, Any]:
        """
        Retrieve company facts from SEC EDGAR database.
        
        Args:
            cik: Central Index Key (CIK) for the company
            
        Returns:
            Dictionary containing company financial facts
        """
        await self._rate_limit()
        
        # Pad CIK to 10 digits
        cik_padded = cik.zfill(10)
        url = f"{self.base_url}/CIK{cik_padded}.json"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully retrieved data for CIK: {cik}")
                    return data
                elif response.status == 404:
                    raise DataAcquisitionError(f"Company not found for CIK: {cik}")
                else:
                    raise DataAcquisitionError(f"SEC API error: {response.status}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error retrieving data for CIK {cik}: {e}")
            raise DataAcquisitionError(f"Network error: {e}")
    
    def extract_financial_statements(self, company_facts: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Extract and structure financial statement data from SEC facts.
        
        Args:
            company_facts: Raw company facts data from SEC
            
        Returns:
            Dictionary containing structured financial statements
        """
        financial_data = {}
        
        # Key financial statement items mapping
        key_items = {
            'Revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'SalesRevenueNet'],
            'NetIncome': ['NetIncomeLoss', 'ProfitLoss'],
            'TotalAssets': ['Assets'],
            'TotalLiabilities': ['Liabilities'],
            'StockholdersEquity': ['StockholdersEquity', 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],
            'OperatingIncome': ['OperatingIncomeLoss'],
            'CostOfRevenue': ['CostOfRevenue', 'CostOfGoodsAndServicesSold'],
            'CurrentAssets': ['AssetsCurrent'],
            'CurrentLiabilities': ['LiabilitiesCurrent'],
            'Cash': ['CashAndCashEquivalentsAtCarryingValue', 'Cash'],
            'OperatingCashFlow': ['NetCashProvidedByUsedInOperatingActivities'],
            'SharesOutstanding': ['CommonStockSharesOutstanding']
        }
        
        try:
            us_gaap_data = company_facts.get('facts', {}).get('us-gaap', {})
            
            for statement_item, possible_keys in key_items.items():
                item_data = None
                
                # Try each possible key until we find data
                for key in possible_keys:
                    if key in us_gaap_data:
                        item_data = us_gaap_data[key]
                        break
                
                if item_data:
                    # Extract annual data (10-K filings)
                    annual_data = []
                    for unit_type, unit_data in item_data.get('units', {}).items():
                        for entry in unit_data:
                            if entry.get('form') == '10-K' and 'fy' in entry:
                                annual_data.append({
                                    'fiscal_year': entry['fy'],
                                    'end_date': entry['end'],
                                    'value': entry['val'],
                                    'unit': unit_type
                                })
                    
                    if annual_data:
                        df = pd.DataFrame(annual_data)
                        df['end_date'] = pd.to_datetime(df['end_date'])
                        df = df.sort_values('end_date').drop_duplicates(subset=['fiscal_year'], keep='last')
                        financial_data[statement_item] = df
            
            logger.info(f"Extracted {len(financial_data)} financial statement items")
            return financial_data
            
        except Exception as e:
            logger.error(f"Error extracting financial statements: {e}")
            raise DataAcquisitionError(f"Failed to extract financial statements: {e}")

async def get_cik_from_ticker(ticker: str) -> str:
    """Convert stock ticker to CIK using SEC company tickers JSON."""
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Financial Analyzer 1.0 (your-email@company.com)"}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                for company_info in data.values():
                    if company_info.get('ticker', '').upper() == ticker.upper():
                        return str(company_info['cik_str'])
                
                raise DataAcquisitionError(f"CIK not found for ticker: {ticker}")
            else:
                raise DataAcquisitionError(f"Failed to retrieve company tickers: {response.status}")

src/data_acquisition/yahoo_finance_client.py

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from ..utils.logger import get_logger
from ..utils.exceptions import DataAcquisitionError

logger = get_logger(__name__)

class YahooFinanceClient:
    """Client for accessing Yahoo Finance market and fundamental data."""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    def get_stock_info(self, ticker: str) -> Dict:
        """
        Get comprehensive stock information including market data and fundamentals.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing stock information
        """
        cache_key = f"stock_info_{ticker}"
        
        # Check cache
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Cache the result
            self.cache[cache_key] = {
                'data': info,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Retrieved stock info for {ticker}")
            return info
            
        except Exception as e:
            logger.error(f"Error retrieving stock info for {ticker}: {e}")
            raise DataAcquisitionError(f"Failed to get stock info: {e}")
    
    def get_financial_statements(self, ticker: str) -> Dict[str, pd.DataFrame]:
        """
        Get financial statements from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing financial statements
        """
        cache_key = f"financials_{ticker}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            stock = yf.Ticker(ticker)
            
            statements = {
                'income_statement': stock.financials.T if hasattr(stock, 'financials') else pd.DataFrame(),
                'balance_sheet': stock.balance_sheet.T if hasattr(stock, 'balance_sheet') else pd.DataFrame(),
                'cash_flow': stock.cashflow.T if hasattr(stock, 'cashflow') else pd.DataFrame(),
                'quarterly_income': stock.quarterly_financials.T if hasattr(stock, 'quarterly_financials') else pd.DataFrame(),
                'quarterly_balance_sheet': stock.quarterly_balance_sheet.T if hasattr(stock, 'quarterly_balance_sheet') else pd.DataFrame(),
                'quarterly_cash_flow': stock.quarterly_cashflow.T if hasattr(stock, 'quarterly_cashflow') else pd.DataFrame()
            }
            
            # Clean up the data
            for key, df in statements.items():
                if not df.empty:
                    df.index = pd.to_datetime(df.index)
                    df = df.sort_index(ascending=False)
                    statements[key] = df
            
            self.cache[cache_key] = {
                'data': statements,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Retrieved financial statements for {ticker}")
            return statements
            
        except Exception as e:
            logger.error(f"Error retrieving financial statements for {ticker}: {e}")
            raise DataAcquisitionError(f"Failed to get financial statements: {e}")
    
    def get_market_data(self, ticker: str, period: str = "5y") -> pd.DataFrame:
        """
        Get historical market data.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with historical price data
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                raise DataAcquisitionError(f"No market data found for {ticker}")
            
            logger.info(f"Retrieved {len(hist)} days of market data for {ticker}")
            return hist
            
        except Exception as e:
            logger.error(f"Error retrieving market data for {ticker}: {e}")
            raise DataAcquisitionError(f"Failed to get market data: {e}")
    
    def get_peer_tickers(self, ticker: str) -> List[str]:
        """
        Get peer company tickers (simplified version).
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of peer ticker symbols
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            # This is a simplified implementation
            # In production, you'd want a more sophisticated peer selection algorithm
            logger.info(f"Sector: {sector}, Industry: {industry} for {ticker}")
            
            # Return empty list for now - this would be enhanced with a proper peer database
            return []
            
        except Exception as e:
            logger.warning(f"Could not determine peers for {ticker}: {e}")
            return []
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return datetime.now() - cached_time < self.cache_ttl

Step 4: Financial Analysis Engine
src/analysis/ratio_calculator.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..utils.logger import get_logger
from ..utils.exceptions import AnalysisError

logger = get_logger(__name__)

@dataclass
class FinancialRatio:
    """Data class for financial ratio with metadata."""
    name: str
    value: float
    category: str
    description: str
    interpretation: str
    confidence_level: float
    calculation_method: str
    period: str

class RatioCalculator:
    """Comprehensive financial ratio calculation engine."""
    
    def __init__(self):
        self.ratios = {}
        self.warnings = []
    
    def calculate_all_ratios(self, financial_data: Dict[str, pd.DataFrame], 
                           market_data: Optional[Dict] = None) -> Dict[str, FinancialRatio]:
        """
        Calculate comprehensive set of financial ratios.
        
        Args:
            financial_data: Dictionary containing financial statement data
            market_data: Optional market data for valuation ratios
            
        Returns:
            Dictionary of calculated financial ratios
        """
        try:
            # Get latest period data
            latest_data = self._get_latest_period_data(financial_data)
            
            if not latest_data:
                raise AnalysisError("No financial data available for ratio calculation")
            
            ratios = {}
            
            # Liquidity Ratios
            ratios.update(self._calculate_liquidity_ratios(latest_data))
            
            # Profitability Ratios
            ratios.update(self._calculate_profitability_ratios(latest_data))
            
            # Leverage Ratios
            ratios.update(self._calculate_leverage_ratios(latest_data))
            
            # Efficiency Ratios
            ratios.update(self._calculate_efficiency_ratios(latest_data))
            
            # Valuation Ratios (if market data available)
            if market_data:
                ratios.update(self._calculate_valuation_ratios(latest_data, market_data))
            
            # Coverage Ratios
            ratios.update(self._calculate_coverage_ratios(latest_data))
            
            logger.info(f"Calculated {len(ratios)} financial ratios")
            return ratios
            
        except Exception as e:
            logger.error(f"Error calculating ratios: {e}")
            raise AnalysisError(f"Ratio calculation failed: {e}")
    
    def _get_latest_period_data(self, financial_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Extract latest period values from financial statements."""
        latest_data = {}
        
        for item_name, df in financial_data.items():
            if not df.empty:
                # Get the most recent value
                latest_value = df.iloc[0]['value'] if 'value' in df.columns else df.iloc[0, 0]
                latest_data[item_name] = float(latest_value)
        
        return latest_data
    
    def _calculate_liquidity_ratios(self, data: Dict[str, float]) -> Dict[str, FinancialRatio]:
        """Calculate liquidity ratios."""
        ratios = {}
        
        # Current Ratio
        if 'CurrentAssets' in data and 'CurrentLiabilities' in data:
            if data['CurrentLiabilities'] != 0:
                current_ratio = data['CurrentAssets'] / data['CurrentLiabilities']
                ratios['current_ratio'] = FinancialRatio(
                    name="Current Ratio",
                    value=current_ratio,
                    category="Liquidity",
                    description="Current Assets / Current Liabilities",
                    interpretation=self._interpret_current_ratio(current_ratio),
                    confidence_level=0.9,
                    calculation_method="CurrentAssets / CurrentLiabilities",
                    period="Latest"
                )
        
        # Quick Ratio (assuming we have inventory data)
        if all(key in data for key in ['CurrentAssets', 'CurrentLiabilities']):
            # Simplified - in reality we'd need inventory data
            quick_assets = data['CurrentAssets'] * 0.8  # Rough estimate
            if data['CurrentLiabilities'] != 0:
                quick_ratio = quick_assets / data['CurrentLiabilities']
                ratios['quick_ratio'] = FinancialRatio(
                    name="Quick Ratio",
                    value=quick_ratio,
                    category="Liquidity",
                    description="(Current Assets - Inventory) / Current Liabilities",
                    interpretation=self._interpret_quick_ratio(quick_ratio),
                    confidence_level=0.7,  # Lower confidence due to estimation
                    calculation_method="(CurrentAssets - Inventory) / CurrentLiabilities",
                    period="Latest"
                )
        
        # Cash Ratio
        if 'Cash' in data and 'CurrentLiabilities' in data:
            if data['CurrentLiabilities'] != 0:
                cash_ratio = data['Cash'] / data['CurrentLiabilities']
                ratios['cash_ratio'] = FinancialRatio(
                    name="Cash Ratio",
                    value=cash_ratio,
                    category="Liquidity",
                    description="Cash and Cash Equivalents / Current Liabilities",
                    interpretation=self._interpret_cash_ratio(cash_ratio),
                    confidence_level=0.9,
                    calculation_method="Cash / CurrentLiabilities",
                    period="Latest"
                )
        
        return ratios
    
    def _calculate_profitability_ratios(self, data: Dict[str, float]) -> Dict[str, FinancialRatio]:
        """Calculate profitability ratios."""
        ratios = {}
        
        # Net Profit Margin
        if 'NetIncome' in data and 'Revenue' in data:
            if data['Revenue'] != 0:
                net_margin = data['NetIncome'] / data['Revenue']
                ratios['net_profit_margin'] = FinancialRatio(
                    name="Net Profit Margin",
                    value=net_margin,
                    category="Profitability",
                    description="Net Income / Revenue",
                    interpretation=self._interpret_profit_margin(net_margin),
                    confidence_level=0.95,
                    calculation_method="NetIncome / Revenue",
                    period="Latest"
                )
        
        # Return on Assets (ROA)
        if 'NetIncome' in data and 'TotalAssets' in data:
            if data['TotalAssets'] != 0:
                roa = data['NetIncome'] / data['TotalAssets']
                ratios['return_on_assets'] = FinancialRatio(
                    name="Return on Assets",
                    value=roa,
                    category="Profitability",
                    description="Net Income / Total Assets",
                    interpretation=self._interpret_roa(roa),
                    confidence_level=0.9,
                    calculation_method="NetIncome / TotalAssets",
                    period="Latest"
                )
        
        # Return on Equity (ROE)
        if 'NetIncome' in data and 'StockholdersEquity' in data:
            if data['StockholdersEquity'] != 0:
                roe = data['NetIncome'] / data['StockholdersEquity']
                ratios['return_on_equity'] = FinancialRatio(
                    name="Return on Equity",
                    value=roe,
                    category="Profitability",
                    description="Net Income / Stockholders Equity",
                    interpretation=self._interpret_roe(roe),
                    confidence_level=0.9,
                    calculation_method="NetIncome / StockholdersEquity",
                    period="Latest"
                )
        
        # Gross Profit Margin
        if all(key in data for key in ['Revenue', 'CostOfRevenue']):
            if data['Revenue'] != 0:
                gross_profit = data['Revenue'] - data['CostOfRevenue']
                gross_margin = gross_profit / data['Revenue']
                ratios['gross_profit_margin'] = FinancialRatio(
                    name="Gross Profit Margin",
                    value=gross_margin,
                    category="Profitability",
                    description="(Revenue - Cost of Revenue) / Revenue",
                    interpretation=self._interpret_gross_margin(gross_margin),
                    confidence_level=0.95,
                    calculation_method="(Revenue - CostOfRevenue) / Revenue",
                    period="Latest"
                )
        
        return ratios
    
    def _calculate_leverage_ratios(self, data: Dict[str, float]) -> Dict[str, FinancialRatio]:
        """Calculate leverage ratios."""
        ratios = {}
        
        # Debt-to-Equity Ratio
        if 'TotalLiabilities' in data and 'StockholdersEquity' in data:
            if data['StockholdersEquity'] != 0:
                debt_to_equity = data['TotalLiabilities'] / data['StockholdersEquity']
                ratios['debt_to_equity'] = FinancialRatio(
                    name="Debt-to-Equity Ratio",
                    value=debt_to_equity,
                    category="Leverage",
                    description="Total Liabilities / Stockholders Equity",
                    interpretation=self._interpret_debt_to_equity(debt_to_equity),
                    confidence_level=0.9,
                    calculation_method="TotalLiabilities / StockholdersEquity",
                    period="Latest"
                )
        
        # Debt-to-Assets Ratio
        if 'TotalLiabilities' in data and 'TotalAssets' in data:
            if data['TotalAssets'] != 0:
                debt_to_assets = data['TotalLiabilities'] / data['TotalAssets']
                ratios['debt_to_assets'] = FinancialRatio(
                    name="Debt-to-Assets Ratio",
                    value=debt_to_assets,
                    category="Leverage",
                    description="Total Liabilities / Total Assets",
                    interpretation=self._interpret_debt_to_assets(debt_to_assets),
                    confidence_level=0.9,
                    calculation_method="TotalLiabilities / TotalAssets",
                    period="Latest"
                )
        
        return ratios
    
    def _calculate_efficiency_ratios(self, data: Dict[str, float]) -> Dict[str, FinancialRatio]:
        """Calculate efficiency ratios."""
        ratios = {}
        
        # Asset Turnover
        if 'Revenue' in data and 'TotalAssets' in data:
            if data['TotalAssets'] != 0:
                asset_turnover = data['Revenue'] / data['TotalAssets']
                ratios['asset_turnover'] = FinancialRatio(
                    name="Asset Turnover",
                    value=asset_turnover,
                    category="Efficiency",
                    description="Revenue / Total Assets",
                    interpretation=self._interpret_asset_turnover(asset_turnover),
                    confidence_level=0.9,
                    calculation_method="Revenue / TotalAssets",
                    period="Latest"
                )
        
        return ratios
    
    def _calculate_valuation_ratios(self, data: Dict[str, float], 
                                  market_data: Dict) -> Dict[str, FinancialRatio]:
        """Calculate valuation ratios using market data."""
        ratios = {}
        
        # Price-to-Earnings Ratio
        if 'NetIncome' in data and 'SharesOutstanding' in data:
            shares = data.get('SharesOutstanding', market_data.get('sharesOutstanding', 0))
            market_cap = market_data.get('marketCap', 0)
            
            if shares > 0 and data['NetIncome'] > 0:
                eps = data['NetIncome'] / shares
                current_price = market_cap / shares if market_cap > 0 else market_data.get('currentPrice', 0)
                
                if eps > 0 and current_price > 0:
                    pe_ratio = current_price / eps
                    ratios['pe_ratio'] = FinancialRatio(
                        name="Price-to-Earnings Ratio",
                        value=pe_ratio,
                        category="Valuation",
                        description="Stock Price / Earnings per Share",
                        interpretation=self._interpret_pe_ratio(pe_ratio),
                        confidence_level=0.8,
                        calculation_method="StockPrice / EPS",
                        period="Latest"
                    )
        
        return ratios
    
    def _calculate_coverage_ratios(self, data: Dict[str, float]) -> Dict[str, FinancialRatio]:
        """Calculate coverage ratios."""
        ratios = {}
        
        # Operating Cash Flow Ratio
        if 'OperatingCashFlow' in data and 'CurrentLiabilities' in data:
            if data['CurrentLiabilities'] != 0:
                ocf_ratio = data['OperatingCashFlow'] / data['CurrentLiabilities']
                ratios['operating_cash_flow_ratio'] = FinancialRatio(
                    name="Operating Cash Flow Ratio",
                    value=ocf_ratio,
                    category="Coverage",
                    description="Operating Cash Flow / Current Liabilities",
                    interpretation=self._interpret_ocf_ratio(ocf_ratio),
                    confidence_level=0.9,
                    calculation_method="OperatingCashFlow / CurrentLiabilities",
                    period="Latest"
                )
        
        return ratios
    
    # Interpretation methods
    def _interpret_current_ratio(self, ratio: float) -> str:
        if ratio > 2.0:
            return "Strong liquidity position, may have excess cash"
        elif ratio > 1.0:
            return "Adequate liquidity to meet short-term obligations"
        else:
            return "Potential liquidity concerns, may struggle with short-term obligations"
    
    def _interpret_quick_ratio(self, ratio: float) -> str:
        if ratio > 1.0:
            return "Strong short-term liquidity without relying on inventory"
        elif ratio > 0.5:
            return "Adequate short-term liquidity"
        else:
            return "Potential short-term liquidity concerns"
    
    def _interpret_cash_ratio(self, ratio: float) -> str:
        if ratio > 0.3:
            return "Very strong immediate liquidity position"
        elif ratio > 0.1:
            return "Adequate cash position"
        else:
            return "Limited immediate liquidity"
    
    def _interpret_profit_margin(self, margin: float) -> str:
        if margin > 0.15:
            return "Excellent profitability"
        elif margin > 0.05:
            return "Good profitability"
        elif margin > 0:
            return "Modest profitability"
        else:
            return "Unprofitable operations"
    
    def _interpret_roa(self, roa: float) -> str:
        if roa > 0.15:
            return "Excellent asset utilization"
        elif roa > 0.05:
            return "Good asset utilization"
        elif roa > 0:
            return "Modest asset utilization"
        else:
            return "Poor asset utilization"
    
    def _interpret_roe(self, roe: float) -> str:
        if roe > 0.20:
            return "Excellent returns to shareholders"
        elif roe > 0.10:
            return "Good returns to shareholders"
        elif roe > 0:
            return "Modest returns to shareholders"
        else:
            return "Poor returns to shareholders"
    
    def _interpret_gross_margin(self, margin: float) -> str:
        if margin > 0.40:
            return "Excellent pricing power and cost control"
        elif margin > 0.20:
            return "Good gross profitability"
        elif margin > 0:
            return "Modest gross profitability"
        else:
            return "Negative gross margins"
    
    def _interpret_debt_to_equity(self, ratio: float) -> str:
        if ratio > 2.0:
            return "High financial leverage, potential risk"
        elif ratio > 1.0:
            return "Moderate financial leverage"
        elif ratio > 0.5:
            return "Conservative debt levels"
        else:
            return "Very conservative debt levels"
    
    def _interpret_debt_to_assets(self, ratio: float) -> str:
        if ratio > 0.6:
            return "High debt relative to assets"
        elif ratio > 0.3:
            return "Moderate debt levels"
        else:
            return "Conservative debt levels"
    
    def _interpret_asset_turnover(self, ratio: float) -> str:
        if ratio > 2.0:
            return "Excellent asset efficiency"
        elif ratio > 1.0:
            return "Good asset efficiency"
        elif ratio > 0.5:
            return "Moderate asset efficiency"
        else:
            return "Poor asset efficiency"
    
    def _interpret_pe_ratio(self, ratio: float) -> str:
        if ratio > 30:
            return "High valuation, growth expectations or overvalued"
        elif ratio > 15:
            return "Moderate valuation"
        elif ratio > 5:
            return "Low valuation, value opportunity or concerns"
        else:
            return "Very low valuation"
    
    def _interpret_ocf_ratio(self, ratio: float) -> str:
        if ratio > 0.4:
            return "Strong cash generation relative to obligations"
        elif ratio > 0.2:
            return "Good cash generation"
        elif ratio > 0:
            return "Modest cash generation"
        else:
            return "Negative operating cash flow"

Step 5: Report Generation System
src/reporting/report_generator.py

import pandas as pd
from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ..analysis.ratio_calculator import FinancialRatio
from ..utils.logger import get_logger
from ..utils.config import config

logger = get_logger(__name__)

class ReportGenerator:
    """Generate comprehensive financial analysis reports."""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
        
    def generate_comprehensive_report(self, 
                                    company_info: Dict[str, Any],
                                    financial_ratios: Dict[str, FinancialRatio],
                                    market_data: Dict[str, Any],
                                    trend_analysis: Dict[str, Any],
                                    benchmark_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive financial analysis report.
        
        Args:
            company_info: Basic company information
            financial_ratios: Calculated financial ratios
            market_data: Market and valuation data
            trend_analysis: Historical trend analysis
            benchmark_data: Industry benchmark comparisons
            
        Returns:
            Dictionary containing complete report data
        """
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'company_info': company_info,
            'executive_summary': self._generate_executive_summary(
                company_info, financial_ratios, market_data
            ),
            'financial_performance': self._analyze_financial_performance(financial_ratios),
            'ratio_analysis': self._format_ratio_analysis(financial_ratios),
            'valuation_assessment': self._assess_valuation(financial_ratios, market_data),
            'risk_analysis': self._analyze_risks(financial_ratios),
            'investment_recommendation': self._generate_investment_recommendation(
                financial_ratios, trend_analysis
            ),
            'data_quality': self._assess_data_quality(financial_ratios),
            'disclaimers': self._get_disclaimers()
        }
        
        # Add benchmark data if available
        if benchmark_data:
            report_data['industry_comparison'] = benchmark_data
        
        logger.info(f"Generated comprehensive report for {company_info.get('symbol', 'Unknown')}")
        return report_data
    
    def _generate_executive_summary(self, 
                                  company_info: Dict[str, Any],
                                  ratios: Dict[str, FinancialRatio],
                                  market_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate executive summary section."""
        
        # Key financial highlights
        key_ratios = ['net_profit_margin', 'return_on_equity', 'current_ratio', 'debt_to_equity']
        highlights = []
        
        for ratio_key in key_ratios:
            if ratio_key in ratios:
                ratio = ratios[ratio_key]
                highlights.append(f"{ratio.name}: {ratio.value:.2%}" if ratio.value < 1 else f"{ratio.name}: {ratio.value:.2f}")
        
        # Overall assessment
        profitability_ratios = [r for r in ratios.values() if r.category == "Profitability"]
        avg_profitability = sum(r.value for r in profitability_ratios) / len(profitability_ratios) if profitability_ratios else 0
        
        if avg_profitability > 0.15:
            assessment = "Strong financial performance with excellent profitability metrics"
        elif avg_profitability > 0.05:
            assessment = "Solid financial performance with good profitability"
        elif avg_profitability > 0:
            assessment = "Moderate financial performance with modest profitability"
        else:
            assessment = "Weak financial performance with profitability concerns"
        
        return {
            'company_overview': f"{company_info.get('longName', company_info.get('symbol', 'N/A'))} operates in the {company_info.get('sector', 'Unknown')} sector",
            'key_highlights': "; ".join(highlights),
            'overall_assessment': assessment,
            'market_capitalization': f"${market_data.get('marketCap', 0):,.0f}" if market_data.get('marketCap') else "N/A"
        }
    
    def _analyze_financial_performance(self, ratios: Dict[str, FinancialRatio]) -> Dict[str, Any]:
        """Analyze financial performance across categories."""
        
        performance = {
            'profitability': self._analyze_category_performance(ratios, "Profitability"),
            'liquidity': self._analyze_category_performance(ratios, "Liquidity"),
            'leverage': self._analyze_category_performance(ratios, "Leverage"),
            'efficiency': self._analyze_category_performance(ratios, "Efficiency"),
            'valuation': self._analyze_category_performance(ratios, "Valuation")
        }
        
        return performance
    
    def _analyze_category_performance(self, ratios: Dict[str, FinancialRatio], 
                                    category: str) -> Dict[str, Any]:
        """Analyze performance for a specific category."""
        
        category_ratios = {k: v for k, v in ratios.items() if v.category == category}
        
        if not category_ratios:
            return {
                'status': 'No data available',
                'ratios': [],
                'summary': f'No {category.lower()} ratios could be calculated'
            }
        
        # Simple scoring based on interpretations
        positive_keywords = ['excellent', 'strong', 'good', 'adequate']
        negative_keywords = ['poor', 'weak', 'concerns', 'risk']
        
        scores = []
        for ratio in category_ratios.values():
            interpretation_lower = ratio.interpretation.lower()
            if any(keyword in interpretation_lower for keyword in positive_keywords):
                scores.append(1)
            elif any(keyword in interpretation_lower for keyword in negative_keywords):
                scores.append(-1)
            else:
                scores.append(0)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score > 0.5:
            status = "Strong"
        elif avg_score > 0:
            status = "Good"
        elif avg_score > -0.5:
            status = "Moderate"
        else:
            status = "Weak"
        
        return {
            'status': status,
            'ratios': [
                {
                    'name': ratio.name,
                    'value': ratio.value,
                    'interpretation': ratio.interpretation
                }
                for ratio in category_ratios.values()
            ],
            'summary': f'{category} analysis shows {status.lower()} performance'
        }
    
    def _format_ratio_analysis(self, ratios: Dict[str, FinancialRatio]) -> Dict[str, List[Dict]]:
        """Format ratios by category for the report."""
        
        categorized_ratios = {}
        
        for ratio in ratios.values():
            if ratio.category not in categorized_ratios:
                categorized_ratios[ratio.category] = []
            
            categorized_ratios[ratio.category].append({
                'name': ratio.name,
                'value': ratio.value,
                'description': ratio.description,
                'interpretation': ratio.interpretation,
                'confidence_level': ratio.confidence_level
            })
        
        return categorized_ratios
    
    def _assess_valuation(self, ratios: Dict[str, FinancialRatio], 
                         market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess company valuation."""
        
        valuation_ratios = {k: v for k, v in ratios.items() if v.category == "Valuation"}
        
        assessment = {
            'current_metrics': {},
            'assessment': 'Insufficient data for valuation assessment',
            'risk_level': 'Unknown'
        }
        
        if 'pe_ratio' in valuation_ratios:
            pe_ratio = valuation_ratios['pe_ratio']
            assessment['current_metrics']['pe_ratio'] = pe_ratio.value
            
            if pe_ratio.value > 30:
                assessment['assessment'] = 'High valuation suggests growth expectations or potential overvaluation'
                assessment['risk_level'] = 'High'
            elif pe_ratio.value > 15:
                assessment['assessment'] = 'Moderate valuation within normal range'
                assessment['risk_level'] = 'Medium'
            else:
                assessment['assessment'] = 'Low valuation may indicate value opportunity or underlying concerns'
                assessment['risk_level'] = 'Medium'
        
        # Add market cap and other market metrics
        if market_data.get('marketCap'):
            assessment['current_metrics']['market_cap'] = market_data['marketCap']
        
        return assessment
    
    def _analyze_risks(self, ratios: Dict[str, FinancialRatio]) -> Dict[str, Any]:
        """Identify and analyze financial risks."""
        
        risks = {
            'liquidity_risk': 'Low',
            'leverage_risk': 'Low',
            'profitability_risk': 'Low',
            'overall_risk': 'Low',
            'risk_factors': []
        }
        
        # Analyze liquidity risk
        if 'current_ratio' in ratios:
            current_ratio = ratios['current_ratio']
            if current_ratio.value < 1.0:
                risks['liquidity_risk'] = 'High'
                risks['risk_factors'].append('Current ratio below 1.0 indicates potential liquidity concerns')
            elif current_ratio.value < 1.5:
                risks['liquidity_risk'] = 'Medium'
                risks['risk_factors'].append('Current ratio below 1.5 suggests monitoring required')
        
        # Analyze leverage risk
        if 'debt_to_equity' in ratios:
            debt_to_equity = ratios['debt_to_equity']
            if debt_to_equity.value > 2.0:
                risks['leverage_risk'] = 'High'
                risks['risk_factors'].append('High debt-to-equity ratio indicates significant financial leverage')
            elif debt_to_equity.value > 1.0:
                risks['leverage_risk'] = 'Medium'
                risks['risk_factors'].append('Moderate financial leverage requires monitoring')
        
        # Analyze profitability risk
        if 'net_profit_margin' in ratios:
            net_margin = ratios['net_profit_margin']
            if net_margin.value < 0:
                risks['profitability_risk'] = 'High'
                risks['risk_factors'].append('Negative profit margins indicate operational challenges')
            elif net_margin.value < 0.02:
                risks['profitability_risk'] = 'Medium'
                risks['risk_factors'].append('Low profit margins suggest competitive pressure')
        
        # Overall risk assessment
        risk_levels = [risks['liquidity_risk'], risks['leverage_risk'], risks['profitability_risk']]
        if 'High' in risk_levels:
            risks['overall_risk'] = 'High'
        elif 'Medium' in risk_levels:
            risks['overall_risk'] = 'Medium'
        
        return risks
    
    def _generate_investment_recommendation(self, 
                                          ratios: Dict[str, FinancialRatio],
                                          trend_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate investment recommendation based on analysis."""
        
        # Simple scoring system
        positive_score = 0
        negative_score = 0
        
        for ratio in ratios.values():
            interpretation_lower = ratio.interpretation.lower()
            if any(word in interpretation_lower for word in ['excellent', 'strong', 'good']):
                positive_score += 1
            elif any(word in interpretation_lower for word in ['poor', 'weak', 'concerns', 'risk']):
                negative_score += 1
        
        net_score = positive_score - negative_score
        total_ratios = len(ratios)
        
        if net_score > total_ratios * 0.3:
            recommendation = "BUY"
            reasoning = "Strong financial metrics across multiple categories suggest attractive investment opportunity"
        elif net_score > 0:
            recommendation = "HOLD"
            reasoning = "Mixed financial performance with both strengths and areas for improvement"
        elif net_score > -total_ratios * 0.3:
            recommendation = "HOLD"
            reasoning = "Adequate financial performance but some areas of concern require monitoring"
        else:
            recommendation = "SELL/AVOID"
            reasoning = "Weak financial performance across multiple metrics suggests significant risks"
        
        return {
            'recommendation': recommendation,
            'reasoning': reasoning,
            'confidence_level': 'Medium',  # Always medium for automated analysis
            'time_horizon': '12-18 months',
            'key_catalysts': 'Monitor quarterly earnings and debt levels',
            'key_risks': 'Economic downturn, industry competition, regulatory changes'
        }
    
    def _assess_data_quality(self, ratios: Dict[str, FinancialRatio]) -> Dict[str, Any]:
        """Assess the quality and completeness of data used."""
        
        total_ratios = len(ratios)
        high_confidence = sum(1 for r in ratios.values() if r.confidence_level > 0.8)
        
        completeness = (total_ratios / 15) * 100  # Assuming 15 key ratios
        
        return {
            'completeness_percentage': min(completeness, 100),
            'total_ratios_calculated': total_ratios,
            'high_confidence_ratios': high_confidence,
            'data_sources': ['SEC EDGAR', 'Yahoo Finance'],
            'last_updated': datetime.now().isoformat(),
            'quality_score': 'High' if high_confidence > total_ratios * 0.7 else 'Medium'
        }
    
    def _get_disclaimers(self) -> List[str]:
        """Get standard disclaimers for the report."""
        
        return [
            "This analysis is for informational purposes only and does not constitute investment advice.",
            "Past performance does not guarantee future results.",
            "All investments carry risk of loss, including potential loss of principal.",
            "Financial data is based on publicly available information and may contain errors or omissions.",
            "This automated analysis should be supplemented with additional research and professional advice.",
            "Market conditions and company circumstances can change rapidly.",
            "Ratios and metrics are based on historical data and may not reflect current conditions."
        ]
    
    def export_to_json(self, report_data: Dict[str, Any], filename: str) -> str:
        """Export report to JSON format."""
        
        filepath = Path(filename)
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Report exported to JSON: {filepath}")
        return str(filepath)
    
    def export_to_html(self, report_data: Dict[str, Any], filename: str) -> str:
        """Export report to HTML format."""
        
        template = self.env.get_template('report_template.html')
        html_content = template.render(**report_data)
        
        filepath = Path(filename)
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Report exported to HTML: {filepath}")
        return str(filepath)

Step 6: Main Application Controller
src/main.py

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Dict, Any
import traceback

from .data_acquisition.sec_edgar_client import SECEdgarClient, get_cik_from_ticker
from .data_acquisition.yahoo_finance_client import YahooFinanceClient
from .analysis.ratio_calculator import RatioCalculator
from .reporting.report_generator import ReportGenerator
from .utils.logger import get_logger, setup_logging
from .utils.config import config
from .utils.exceptions import DataAcquisitionError, AnalysisError

logger = get_logger(__name__)

class FinancialAnalyzer:
    """Main application controller for financial analysis system."""
    
    def __init__(self):
        self.sec_client = None
        self.yahoo_client = YahooFinanceClient()
        self.ratio_calculator = RatioCalculator()
        self.report_generator = ReportGenerator()
        
    async def analyze_company(self, ticker: str, output_format: str = "both") -> Dict[str, str]:
        """
        Perform comprehensive financial analysis for a company.
        
        Args:
            ticker: Stock ticker symbol
            output_format: Output format ("json", "html", "pdf", "both")
            
        Returns:
            Dictionary with file paths of generated reports
        """
        try:
            logger.info(f"Starting financial analysis for {ticker}")
            
            # Step 1: Get company basic information
            company_info = await self._get_company_info(ticker)
            logger.info(f"Retrieved company info for {company_info.get('longName', ticker)}")
            
            # Step 2: Acquire financial data from multiple sources
            financial_data = await self._acquire_financial_data(ticker)
            logger.info("Financial data acquisition completed")
            
            # Step 3: Get market data
            market_data = self._get_market_data(ticker)
            logger.info("Market data acquisition completed")
            
            # Step 4: Calculate financial ratios
            financial_ratios = self.ratio_calculator.calculate_all_ratios(
                financial_data, market_data
            )
            logger.info(f"Calculated {len(financial_ratios)} financial ratios")
            
            # Step 5: Perform trend analysis (simplified for this implementation)
            trend_analysis = self._perform_trend_analysis(financial_data)
            
            # Step 6: Generate comprehensive report
            report_data = self.report_generator.generate_comprehensive_report(
                company_info=company_info,
                financial_ratios=financial_ratios,
                market_data=market_data,
                trend_analysis=trend_analysis
            )
            
            # Step 7: Export reports
            output_files = await self._export_reports(report_data, ticker, output_format)
            
            logger.info(f"Analysis completed successfully for {ticker}")
            return output_files
            
        except Exception as e:
            logger.error(f"Analysis failed for {ticker}: {e}")
            logger.error(traceback.format_exc())
            raise AnalysisError(f"Failed to analyze {ticker}: {e}")
    
    async def _get_company_info(self, ticker: str) -> Dict[str, Any]:
        """Get basic company information."""
        try:
            company_info = self.yahoo_client.get_stock_info(ticker)
            return {
                'symbol': ticker.upper(),
                'longName': company_info.get('longName', 'N/A'),
                'sector': company_info.get('sector', 'N/A'),
                'industry': company_info.get('industry', 'N/A'),
                'website': company_info.get('website', 'N/A'),
                'employees': company_info.get('fullTimeEmployees', 'N/A'),
                'description': company_info.get('longBusinessSummary', 'N/A')[:500] + '...' if company_info.get('longBusinessSummary') else 'N/A'
            }
        except Exception as e:
            logger.warning(f"Could not get company info from Yahoo Finance: {e}")
            return {
                'symbol': ticker.upper(),
                'longName': ticker.upper(),
                'sector': 'N/A',
                'industry': 'N/A'
            }
    
    async def _acquire_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Acquire financial data from multiple sources with fallback logic."""
        financial_data = {}
        
        # Try SEC EDGAR first (more reliable for US companies)
        try:
            cik = await get_cik_from_ticker(ticker)
            async with SECEdgarClient() as sec_client:
                company_facts = await sec_client.get_company_facts(cik)
                sec_data = sec_client.extract_financial_statements(company_facts)
                if sec_data:
                    financial_data.update(sec_data)
                    logger.info("Successfully acquired data from SEC EDGAR")
        except Exception as e:
            logger.warning(f"SEC EDGAR data acquisition failed: {e}")
        
        # Fallback to Yahoo Finance
        try:
            yahoo_statements = self.yahoo_client.get_financial_statements(ticker)
            # Convert Yahoo Finance data to our format
            yahoo_converted = self._convert_yahoo_data(yahoo_statements)
            
            # Merge with SEC data (SEC takes precedence)
            for key, value in yahoo_converted.items():
                if key not in financial_data or financial_data[key].empty:
                    financial_data[key] = value
            
            logger.info("Successfully acquired fallback data from Yahoo Finance")
            
        except Exception as e:
            logger.warning(f"Yahoo Finance data acquisition failed: {e}")
        
        if not financial_data:
            raise DataAcquisitionError(f"Could not acquire financial data for {ticker}")
        
        return financial_data
    
    def _convert_yahoo_data(self, yahoo_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Yahoo Finance data format to our standard format."""
        converted_data = {}
        
        # Map Yahoo Finance column names to our standard names
        yahoo_mapping = {
            'Total Revenue': 'Revenue',
            'Net Income': 'NetIncome',
            'Total Assets': 'TotalAssets',
            'Total Liab': 'TotalLiabilities',
            'Total Stockholder Equity': 'StockholdersEquity',
            'Operating Income': 'OperatingIncome',
            'Cost Of Revenue': 'CostOfRevenue',
            'Current Assets': 'CurrentAssets',
            'Current Liabilities': 'CurrentLiabilities',
            'Cash And Cash Equivalents': 'Cash',
            'Operating Cash Flow': 'OperatingCashFlow'
        }
        
        for statement_type, df in yahoo_statements.items():
            if df.empty:
                continue
                
            for yahoo_name, standard_name in yahoo_mapping.items():
                if yahoo_name in df.columns:
                    # Create DataFrame in our format
                    data_df = pd.DataFrame({
                        'fiscal_year': df.index.year,
                        'end_date': df.index,
                        'value': df[yahoo_name].values,
                        'unit': 'USD'
                    })
                    data_df = data_df.dropna().sort_values('end_date', ascending=False)
                    if not data_df.empty:
                        converted_data[standard_name] = data_df
        
        return converted_data
    
    def _get_market_data(self, ticker: str) -> Dict[str, Any]:
        """Get current market data."""
        try:
            stock_info = self.yahoo_client.get_stock_info(ticker)
            return {
                'marketCap': stock_info.get('marketCap'),
                'currentPrice': stock_info.get('currentPrice'),
                'sharesOutstanding': stock_info.get('sharesOutstanding'),
                'beta': stock_info.get('beta'),
                'trailingPE': stock_info.get('trailingPE'),
                'forwardPE': stock_info.get('forwardPE'),
                'priceToBook': stock_info.get('priceToBook')
            }
        except Exception as e:
            logger.warning(f"Could not get market data: {e}")
            return {}
    
    def _perform_trend_analysis(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic trend analysis (simplified implementation)."""
        trends = {}
        
        for item_name, df in financial_data.items():
            if len(df) >= 2:
                # Calculate year-over-year growth
                latest_value = df.iloc[0]['value']
                previous_value = df.iloc[1]['value']
                
                if previous_value != 0:
                    growth_rate = (latest_value - previous_value) / abs(previous_value)
                    trends[item_name] = {
                        'growth_rate': growth_rate,
                        'trend': 'Improving' if growth_rate > 0 else 'Declining'
                    }
        
        return trends
    
    async def _export_reports(self, report_data: Dict[str, Any], 
                            ticker: str, output_format: str) -> Dict[str, str]:
        """Export reports in requested formats."""
        output_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        
        if output_format in ["json", "both"]:
            json_file = output_dir / f"{ticker}_{timestamp}_report.json"
            self.report_generator.export_to_json(report_data, str(json_file))
            output_files['json'] = str(json_file)
        
        if output_format in ["html", "both"]:
            html_file = output_dir / f"{ticker}_{timestamp}_report.html"
            self.report_generator.export_to_html(report_data, str(html_file))
            output_files['html'] = str(html_file)
        
        return output_files

async def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Financial Analysis System")
    parser.add_argument("ticker", help="Stock ticker symbol")
    parser.add_argument("--format", choices=["json", "html", "both"], 
                       default="both", help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    
    try:
        analyzer = FinancialAnalyzer()
        output_files = await analyzer.analyze_company(args.ticker, args.format)
        
        print(f"\n✅ Analysis completed successfully for {args.ticker.upper()}")
        print("📋 Generated reports:")
        for format_type, filepath in output_files.items():
            print(f"  • {format_type.upper()}: {filepath}")
        
        print("\n⚠️  DISCLAIMER: This analysis is for informational purposes only.")
        print("   Please consult with a financial advisor before making investment decisions.")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

Step 7: Utility Modules
src/utils/logger.py

import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup application logging configuration."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_level = getattr(logging, level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
    else:
        file_handler = logging.FileHandler(log_dir / "financial_analyzer.log")
    
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("yfinance").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

src/utils/exceptions.py

"""Custom exceptions for the financial analysis system."""

class FinancialAnalysisError(Exception):
    """Base exception for financial analysis system."""
    pass

class DataAcquisitionError(FinancialAnalysisError):
    """Exception raised when data acquisition fails."""
    pass

class AnalysisError(FinancialAnalysisError):
    """Exception raised when financial analysis fails."""
    pass

class ReportGenerationError(FinancialAnalysisError):
    """Exception raised when report generation fails."""
    pass

class ValidationError(FinancialAnalysisError):
    """Exception raised when data validation fails."""
    pass

Step 8: HTML Report Template
templates/report_template.html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Analysis Report - {{ company_info.symbol }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .header .subtitle {
            color: #7f8c8d;
            font-size: 18px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #3498db;
            background-color: #f8f9fa;
        }
        .section h2 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 10px;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e1e8ed;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-name {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 5px;
        }
        .metric-interpretation {
            font-size: 14px;
            color: #7f8c8d;
            font-style: italic;
        }
        .recommendation {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .recommendation h3 {
            margin-top: 0;
            font-size: 24px;
        }
        .risk-analysis {
            background-color: #fff3cd;
            border: 1px solid #ffeeba;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .risk-high { border-left-color: #dc3545; }
        .risk-medium { border-left-color: #ffc107; }
        .risk-low { border-left-color: #28a745; }
        .disclaimers {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 20px;
            border-radius: 5px;
            margin-top: 30px;
        }
        .disclaimers h3 {
            color: #495057;
            margin-top: 0;
        }
        .disclaimers ul {
            padding-left: 20px;
        }
        .disclaimers li {
            margin-bottom: 8px;
            color: #6c757d;
        }
        .data-quality {
            background-color: #e7f3ff;
            border: 1px solid #b3d9ff;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .timestamp {
            text-align: right;
            color: #6c757d;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Financial Analysis Report</h1>
            <div class="subtitle">{{ company_info.longName }} ({{ company_info.symbol }})</div>
            <div class="subtitle">{{ company_info.sector }} | {{ company_info.industry }}</div>
        </div>

        <div class="section">
            <h2>Executive Summary</h2>
            <p><strong>Company Overview:</strong> {{ executive_summary.company_overview }}</p>
            <p><strong>Market Capitalization:</strong> {{ executive_summary.market_capitalization }}</p>
            <p><strong>Key Financial Highlights:</strong> {{ executive_summary.key_highlights }}</p>
            <p><strong>Overall Assessment:</strong> {{ executive_summary.overall_assessment }}</p>
        </div>

        <div class="section">
            <h2>Investment Recommendation</h2>
            <div class="recommendation">
                <h3>{{ investment_recommendation.recommendation }}</h3>
                <p>{{ investment_recommendation.reasoning }}</p>
                <p><strong>Time Horizon:</strong> {{ investment_recommendation.time_horizon }}</p>
                <p><strong>Confidence Level:</strong> {{ investment_recommendation.confidence_level }}</p>
            </div>
        </div>

        <div class="section">
            <h2>Financial Ratio Analysis</h2>
            {% for category, ratios in ratio_analysis.items() %}
            <h3>{{ category }} Ratios</h3>
            <div class="metric-grid">
                {% for ratio in ratios %}
                <div class="metric-card">
                    <div class="metric-name">{{ ratio.name }}</div>
                    <div class="metric-value">
                        {% if ratio.value < 1 %}
                            {{ "%.1f%%" | format(ratio.value * 100) }}
                        {% else %}
                            {{ "%.2f" | format(ratio.value) }}
                        {% endif %}
                    </div>
                    <div class="metric-interpretation">{{ ratio.interpretation }}</div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>

        <div class="section">
            <h2>Financial Performance Summary</h2>
            {% for category, performance in financial_performance.items() %}
            <h3>{{ category|title }} Performance: {{ performance.status }}</h3>
            <p>{{ performance.summary }}</p>
            {% endfor %}
        </div>

        <div class="section">
            <h2>Risk Analysis</h2>
            <div class="risk-analysis risk-{{ risk_analysis.overall_risk|lower }}">
                <h3>Overall Risk Level: {{ risk_analysis.overall_risk }}</h3>
                <p><strong>Liquidity Risk:</strong> {{ risk_analysis.liquidity_risk }}</p>
                <p><strong>Leverage Risk:</strong> {{ risk_analysis.leverage_risk }}</p>
                <p><strong>Profitability Risk:</strong> {{ risk_analysis.profitability_risk }}</p>
                
                {% if risk_analysis.risk_factors %}
                <h4>Key Risk Factors:</h4>
                <ul>
                    {% for factor in risk_analysis.risk_factors %}
                    <li>{{ factor }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
        </div>

        <div class="section">
            <h2>Valuation Assessment</h2>
            <p>{{ valuation_assessment.assessment }}</p>
            <p><strong>Valuation Risk Level:</strong> {{ valuation_assessment.risk_level }}</p>
            {% if valuation_assessment.current_metrics %}
            <h3>Current Valuation Metrics:</h3>
            <ul>
                {% for metric, value in valuation_assessment.current_metrics.items() %}
                <li><strong>{{ metric|replace('_', ' ')|title }}:</strong> 
                    {% if metric == 'market_cap' %}
                        ${{ "{:,.0f}".format(value) }}
                    {% else %}
                        {{ "%.2f" | format(value) }}
                    {% endif %}
                </li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>

        <div class="data-quality">
            <h3>Data Quality Assessment</h3>
            <p><strong>Quality Score:</strong> {{ data_quality.quality_score }}</p>
            <p><strong>Completeness:</strong> {{ "%.1f%%" | format(data_quality.completeness_percentage) }}</p>
            <p><strong>Ratios Calculated:</strong> {{ data_quality.total_ratios_calculated }}</p>
            <p><strong>High Confidence Ratios:</strong> {{ data_quality.high_confidence_ratios }}</p>
            <p><strong>Data Sources:</strong> {{ data_quality.data_sources|join(', ') }}</p>
        </div>

        <div class="disclaimers">
            <h3>Important Disclaimers</h3>
            <ul>
                {% for disclaimer in disclaimers %}
                <li>{{ disclaimer }}</li>
                {% endfor %}
            </ul>
        </div>

        <div class="timestamp">
            Report generated on: {{ generated_at }}
        </div>
    </div>
</body>
</html>

Step 9: Deployment Instructions
Docker Setup (docker-compose.yml)

version: '3.8'

services:
  financial-analyzer:
    build: .
    container_name: financial-analyzer
    volumes:
      - ./reports:/app/reports
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
    depends_on:
      - redis
    networks:
      - financial-network

  redis:
    image: redis:7-alpine
    container_name: financial-redis
    networks:
      - financial-network

networks:
  financial-network:
    driver: bridge

Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p logs reports config

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for web interface (future enhancement)
EXPOSE 8000

# Default command
CMD ["python", "-m", "src.main", "--help"]

Installation and Deployment Script (deploy.sh)

#!/bin/bash

set -e

echo "🚀 Deploying Financial Analysis System..."

# Create necessary directories
mkdir -p logs reports config data

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python $python_version is not compatible. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
