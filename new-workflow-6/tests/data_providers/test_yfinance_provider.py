# File: tests/data_providers/test_yfinance_provider.py
# Purpose: Unit tests for the YFinanceProvider.

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from financial_analysis.data_providers.yfinance_provider import YFinanceProvider
from financial_analysis.data_providers.base_provider import DataProviderError
from financial_analysis.core.models import CompanyInfo, FinancialStatement

@pytest.fixture
def mock_yf_ticker():
    """A pytest fixture to mock the yfinance.Ticker object."""
    # Mock data that mimics the real yfinance output
    mock_info = {
        'longName': 'MockTech Inc.',
        'exchange': 'MOCK',
        'sector': 'Technology',
        'industry': 'Software - Infrastructure',
        'longBusinessSummary': 'MockTech Inc. provides mock software solutions.',
        'website': 'http://mocktech.com',
        'trailingPegRatio': 1.5 # Used as a key to check for valid data
    }
    
    date_cols = [datetime(2023, 12, 31), datetime(2022, 12, 31)]
    
    mock_financials = pd.DataFrame({
        'Total Revenue': [1000, 900],
        'Gross Profit': [800, 700],
        'Net Income': [200, 150]
    }, index=date_cols).T
    
    mock_balance_sheet = pd.DataFrame({
        'Total Assets': [5000, 4500],
        'Current Assets': [2000, 1800],
        'Total Debt': [1000, 950]
    }, index=date_cols).T
    
    mock_cashflow = pd.DataFrame({
        'Operating Cash Flow': [500, 450],
        'Capital Expenditure': [100, 90]
    }, index=date_cols).T

    # Create a mock object that has the 'info' attribute and methods
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.info = mock_info
    mock_ticker_instance.financials = mock_financials
    mock_ticker_instance.balance_sheet = mock_balance_sheet
    mock_ticker_instance.cashflow = mock_cash_flow
    
    # Use patch to replace yfinance.Ticker with our mock
    with patch('yfinance.Ticker', return_value=mock_ticker_instance) as mock:
        yield mock

def test_get_company_info_success(mock_yf_ticker):
    """Tests successful fetching of company info."""
    provider = YFinanceProvider()
    info = provider.get_company_info("MOCK")
    
    assert isinstance(info, CompanyInfo)
    assert info.name == "MockTech Inc."
    assert info.sector == "Technology"
    assert info.description is not None
    assert info.cik is None # yfinance does not provide CIK

def test_get_company_info_invalid_ticker(mock_yf_ticker):
    """Tests that a DataProviderError is raised for an invalid ticker."""
    # Configure the mock to return an empty dict for the 'info' attribute
    mock_yf_ticker.return_value.info = {}
    
    provider = YFinanceProvider()
    with pytest.raises(DataProviderError, match="yfinance returned no valid data"):
        provider.get_company_info("INVALID")

def test_get_financial_statements_success(mock_yf_ticker):
    """Tests successful fetching and parsing of financial statements."""
    provider = YFinanceProvider()
    statements = provider.get_financial_statements("MOCK", num_years=2)
    
    assert isinstance(statements, list)
    assert len(statements) == 2
    
    # Check the most recent statement (2023)
    stmt_2023 = statements[0]
    assert isinstance(stmt_2023, FinancialStatement)
    assert stmt_2023.fiscal_year == 2023
    assert stmt_2023.income_statement.revenue == 1000
    assert stmt_2023.balance_sheet.total_assets == 5000
    assert stmt_2023.cash_flow_statement.operating_cash_flow == 500
    
    # Check the older statement (2022)
    stmt_2022 = statements[1]
    assert stmt_2022.fiscal_year == 2022
    assert stmt_2022.income_statement.revenue == 900

def test_get_financial_statements_missing_data(mock_yf_ticker):
    """Tests that missing data points are gracefully handled as None."""
    # Modify the mock to remove a metric
    mock_yf_ticker.return_value.financials = mock_yf_ticker.return_value.financials.drop('Gross Profit')
    
    provider = YFinanceProvider()
    statements = provider.get_financial_statements("MOCK", num_years=1)
    
    assert statements[0].income_statement.gross_profit is None
    assert statements[0].income_statement.revenue == 1000 # Other data is still present

def test_get_financial_statements_empty_dataframe(mock_yf_ticker):
    """Tests that an error is raised if yfinance returns empty dataframes."""
    mock_yf_ticker.return_value.financials = pd.DataFrame()
    
    provider = YFinanceProvider()
    with pytest.raises(DataProviderError, match="yfinance returned empty financial statements"):
        provider.get_financial_statements("EMPTY", num_years=2)
