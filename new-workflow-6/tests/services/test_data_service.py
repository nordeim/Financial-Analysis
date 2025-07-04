# File: tests/services/test_data_service.py
# Purpose: Unit tests for the DataService.

import pytest
from typing import List

from financial_analysis.services.data_service import DataService
from financial_analysis.data_providers.base_provider import BaseDataProvider, DataProviderError
from financial_analysis.core.models import CompanyInfo, FinancialStatement, IncomeStatement, BalanceSheet, CashFlowStatement
from datetime import datetime

# --- Mock Providers for Testing ---

class MockProvider(BaseDataProvider):
    """A configurable mock provider for testing the DataService."""
    def __init__(self, name: str, info: CompanyInfo, statements: List[FinancialStatement], should_fail: bool = False):
        self.name = name
        self._info = info
        self._statements = statements
        self._should_fail = should_fail
    
    def get_company_info(self, ticker: str) -> CompanyInfo:
        if self._should_fail:
            raise DataProviderError(f"{self.name} failed to get info")
        return self._info

    def get_financial_statements(self, ticker: str, num_years: int) -> List[FinancialStatement]:
        if self._should_fail:
            raise DataProviderError(f"{self.name} failed to get statements")
        return self._statements

# --- Test Fixtures ---

@pytest.fixture
def empty_statement():
    """An empty FinancialStatement for placeholder use."""
    return FinancialStatement(
        ticker="TEST", period="FY", fiscal_year=2023, end_date=datetime.now(),
        source_url="", income_statement=IncomeStatement(),
        balance_sheet=BalanceSheet(), cash_flow_statement=CashFlowStatement()
    )

@pytest.fixture
def primary_provider(empty_statement):
    """A mock primary provider (like SEC) with good statements but basic info."""
    info = CompanyInfo(ticker="TEST", name="Primary Name", sector=None)
    statements = [empty_statement]
    return MockProvider(name="Primary", info=info, statements=statements)
    
@pytest.fixture
def enrichment_provider(empty_statement):
    """A mock enrichment provider (like yfinance) with rich info but basic statements."""
    info = CompanyInfo(ticker="TEST", name="Enrichment Name", sector="Technology", industry="Software")
    statements = [empty_statement] # Has statements, but they won't be used if primary succeeds
    return MockProvider(name="Enrichment", info=info, statements=statements)

@pytest.fixture
def failing_provider():
    """A mock provider that always fails."""
    return MockProvider(name="Failing", info=None, statements=None, should_fail=True)

# --- Test Cases ---

def test_primary_provider_succeeds(primary_provider, enrichment_provider):
    """Tests that statements are taken from the first provider if it succeeds."""
    service = DataService(providers=[primary_provider, enrichment_provider])
    info, stmts = service.fetch_company_financials("TEST", 1)
    
    # The 'name' should be from the primary provider, not overwritten
    assert info.name == "Primary Name"
    # The 'sector' should be filled in from the enrichment provider
    assert info.sector == "Technology"
    # Statements should be from the primary provider
    assert len(stmts) == 1

def test_fallback_provider_succeeds(primary_provider, failing_provider):
    """Tests that the service falls back to the next provider if the first fails."""
    service = DataService(providers=[failing_provider, primary_provider])
    info, stmts = service.fetch_company_financials("TEST", 1)
    
    assert info.name == "Primary Name"
    assert len(stmts) == 1
    
def test_all_providers_fail(failing_provider):
    """Tests that a DataProviderError is raised if all providers fail."""
    service = DataService(providers=[failing_provider, failing_provider])
    with pytest.raises(DataProviderError, match="Could not retrieve financial statements"):
        service.fetch_company_financials("TEST", 1)

def test_enrichment_fills_missing_data(primary_provider, enrichment_provider):
    """Tests the core enrichment logic of filling in None fields."""
    service = DataService(providers=[primary_provider, enrichment_provider])
    info, stmts = service.fetch_company_financials("TEST", 1)
    
    assert info.ticker == "TEST"
    assert info.name == "Primary Name"       # Value from primary is kept
    assert info.sector == "Technology"      # Value from enrichment is added
    assert info.industry == "Software"      # Value from enrichment is added

def test_enrichment_does_not_require_all_providers_to_succeed(primary_provider, failing_provider):
    """Tests that enrichment continues even if one enrichment provider fails."""
    service = DataService(providers=[primary_provider, failing_provider])
    info, stmts = service.fetch_company_financials("TEST", 1)
    
    # The process should complete successfully using only the primary provider's data
    assert info.name == "Primary Name"
    assert info.sector is None # No enrichment data was available
