# File: src/financial_analysis/data_providers/yfinance_provider.py
# Purpose: Implements a data provider using the yfinance library.

import yfinance as yf
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..core.models import (
    CompanyInfo, FinancialStatement, IncomeStatement, BalanceSheet, CashFlowStatement
)
from .base_provider import BaseDataProvider, DataProviderError

logger = logging.getLogger(__name__)

# Mapping from yfinance data keys to our Pydantic model fields
# Using .get() on the series is crucial as not all fields are present for all companies
YFINANCE_INCOME_MAP = {
    "revenue": "Total Revenue",
    "cost_of_goods_sold": "Cost Of Revenue",
    "gross_profit": "Gross Profit",
    "operating_income": "Operating Income",
    "interest_expense": "Interest Expense",
    "net_income": "Net Income",
    "ebitda": "EBITDA",
    "eps_basic": "Basic EPS",
    "eps_diluted": "Diluted EPS",
}

YFINANCE_BALANCE_MAP = {
    "total_assets": "Total Assets",
    "current_assets": "Current Assets",
    "cash_and_equivalents": "Cash And Cash Equivalents",
    "inventory": "Inventory",
    "accounts_receivable": "Accounts Receivable",
    "total_liabilities": "Total Liabilities Net Minority Interest",
    "current_liabilities": "Current Liabilities",
    "total_debt": "Total Debt",
    "shareholders_equity": "Stockholders Equity",
    "shares_outstanding": "Share Issued", # yfinance provides 'Share Issued'
}

YFINANCE_CASHFLOW_MAP = {
    "operating_cash_flow": "Operating Cash Flow",
    "capital_expenditures": "Capital Expenditure",
    "free_cash_flow": "Free Cash Flow",
    "dividend_payments": "Cash Dividends Paid",
}


class YFinanceProvider(BaseDataProvider):
    """Provides financial data by fetching it from Yahoo Finance via the yfinance library."""

    def get_company_info(self, ticker: str) -> CompanyInfo:
        """Fetches general company information for a given ticker."""
        logger.info(f"Getting company info for {ticker} from yfinance.")
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            
            if not info or info.get('trailingPegRatio') is None: # A simple check for a valid ticker response
                raise DataProviderError(f"yfinance returned no valid data for ticker '{ticker}'. It may be delisted or invalid.")

            return CompanyInfo(
                ticker=ticker.upper(),
                name=info.get('longName'),
                exchange=info.get('exchange'),
                sector=info.get('sector'),
                industry=info.get('industry'),
                description=info.get('longBusinessSummary'),
                website=info.get('website'),
                cik=None # yfinance does not provide CIK
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching info for '{ticker}' from yfinance: {e}")
            raise DataProviderError(f"Failed to get company info for '{ticker}' from yfinance.") from e

    def get_financial_statements(self, ticker: str, num_years: int) -> List[FinancialStatement]:
        """Fetches historical financial statements for a given ticker."""
        logger.info(f"Getting financial statements for {ticker} from yfinance.")
        try:
            ticker_obj = yf.Ticker(ticker)
            
            # Fetch all statements. yfinance returns them as pandas DataFrames.
            income_stmt_df = ticker_obj.financials
            balance_sheet_df = ticker_obj.balance_sheet
            cash_flow_df = ticker_obj.cashflow

            if income_stmt_df.empty or balance_sheet_df.empty:
                raise DataProviderError(f"yfinance returned empty financial statements for '{ticker}'.")

            statements = []
            # Columns are datetime objects representing the period end date
            for year_col in income_stmt_df.columns[:num_years]:
                fy = year_col.year
                
                def get_val(df: pd.DataFrame, key_map: Dict, our_key: str) -> Optional[float]:
                    """Safely gets a value from a DataFrame column for a given year."""
                    yf_key = key_map.get(our_key)
                    if not yf_key or yf_key not in df.index:
                        return None
                    
                    val = df.loc[yf_key].get(year_col)
                    return float(val) if pd.notna(val) else None

                income_data = {key: get_val(income_stmt_df, YFINANCE_INCOME_MAP, key) for key in YFINANCE_INCOME_MAP}
                balance_data = {key: get_val(balance_sheet_df, YFINANCE_BALANCE_MAP, key) for key in YFINANCE_BALANCE_MAP}
                cash_flow_data = {key: get_val(cash_flow_df, YFINANCE_CASHFLOW_MAP, key) for key in YFINANCE_CASHFLOW_MAP}

                stmt = FinancialStatement(
                    ticker=ticker.upper(),
                    period="FY",
                    fiscal_year=fy,
                    end_date=year_col,
                    source_url="https://finance.yahoo.com",
                    income_statement=IncomeStatement(**income_data),
                    balance_sheet=BalanceSheet(**balance_data),
                    cash_flow_statement=CashFlowStatement(**cash_flow_data)
                )
                statements.append(stmt)
                
            if not statements:
                raise DataProviderError(f"Could not construct any statements for '{ticker}' from yfinance data.")
            
            return statements

        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching statements for '{ticker}' from yfinance: {e}")
            raise DataProviderError(f"Failed to get financial statements for '{ticker}' from yfinance.") from e
