# File: src/financial_analysis/core/models.py
# Purpose: Defines the canonical, strictly-typed data structures for the entire application.
# Using Pydantic models ensures data integrity and validation at runtime.

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# It's good practice to use aliases for long XBRL-like names to keep our code clean,
# while still being able to parse data from sources that use those names.

class IncomeStatement(BaseModel):
    """Data model for a single period's Income Statement."""
    revenue: Optional[float] = Field(None, description="Total Revenue or Sales")
    cost_of_goods_sold: Optional[float] = Field(None, description="Cost of Goods Sold (COGS)")
    gross_profit: Optional[float] = Field(None, description="Gross Profit (Revenue - COGS)")
    operating_income: Optional[float] = Field(None, description="Operating Income or EBIT")
    interest_expense: Optional[float] = Field(None, description="Interest Expense")
    net_income: Optional[float] = Field(None, description="Net Income")
    ebitda: Optional[float] = Field(None, description="Earnings Before Interest, Taxes, Depreciation, and Amortization")
    eps_basic: Optional[float] = Field(None, description="Basic Earnings Per Share")
    eps_diluted: Optional[float] = Field(None, description="Diluted Earnings Per Share")

class BalanceSheet(BaseModel):
    """Data model for a single period's Balance Sheet."""
    total_assets: Optional[float] = Field(None, description="Total Assets")
    current_assets: Optional[float] = Field(None, description="Total Current Assets")
    cash_and_equivalents: Optional[float] = Field(None, description="Cash and Cash Equivalents")
    inventory: Optional[float] = Field(None, description="Inventory")
    accounts_receivable: Optional[float] = Field(None, description="Accounts Receivable")
    
    total_liabilities: Optional[float] = Field(None, description="Total Liabilities")
    current_liabilities: Optional[float] = Field(None, description="Total Current Liabilities")
    
    total_debt: Optional[float] = Field(None, description="Total Debt (Short-term and Long-term)")
    shareholders_equity: Optional[float] = Field(None, description="Total Shareholders' Equity")
    shares_outstanding: Optional[float] = Field(None, description="Weighted Average Shares Outstanding")

class CashFlowStatement(BaseModel):
    """Data model for a single period's Cash Flow Statement."""
    operating_cash_flow: Optional[float] = Field(None, description="Net Cash Flow from Operating Activities")
    capital_expenditures: Optional[float] = Field(None, description="Capital Expenditures (CapEx)")
    free_cash_flow: Optional[float] = Field(None, description="Free Cash Flow (OCF - CapEx)")
    dividend_payments: Optional[float] = Field(None, description="Cash Paid for Dividends")

class FinancialStatement(BaseModel):
    """Composite model for a full financial statement for one period."""
    # Metadata
    ticker: str
    period: str = Field(..., description="Reporting period, e.g., 'FY', 'Q1', 'Q2'")
    fiscal_year: int
    end_date: datetime
    
    # Financial Statements
    income_statement: IncomeStatement
    balance_sheet: BalanceSheet
    cash_flow_statement: CashFlowStatement
    
    # Source Tracking
    source_url: str
    retrieval_date: datetime = Field(default_factory=datetime.utcnow)

class FinancialRatios(BaseModel):
    """Data model for all calculated financial ratios for one period."""
    # Metadata
    ticker: str
    period: str
    fiscal_year: int
    
    # Liquidity Ratios
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    
    # Profitability Ratios
    roe: Optional[float] = Field(None, description="Return on Equity")
    roa: Optional[float] = Field(None, description="Return on Assets")
    gross_margin: Optional[float] = None
    net_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    
    # Leverage Ratios
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    times_interest_earned: Optional[float] = None
    debt_service_coverage: Optional[float] = None
    
    # Efficiency Ratios
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None

class CompanyInfo(BaseModel):
    """Data model for general company information."""
    ticker: str
    name: str
    exchange: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    cik: Optional[str] = None

class CompanyAnalysis(BaseModel):
    """The final, top-level data model for a complete company analysis report."""
    company_info: CompanyInfo
    historical_statements: List[FinancialStatement]
    historical_ratios: List[FinancialRatios]
    qualitative_analysis: Dict[str, Any] # MODIFIED: Changed from Dict[str, str] to Dict[str, Any] to accommodate lists for strengths/concerns.
    
    # Report Metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    data_sources_used: List[str]

