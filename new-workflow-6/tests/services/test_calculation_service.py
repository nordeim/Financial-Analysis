# File: tests/services/test_calculation_service.py
# Purpose: Unit tests for the CalculationService to ensure financial ratios are calculated correctly.

import pytest
from datetime import datetime

from financial_analysis.core.models import (
    FinancialStatement, IncomeStatement, BalanceSheet, CashFlowStatement
)
from financial_analysis.services.calculation_service import CalculationService

@pytest.fixture
def sample_statement() -> FinancialStatement:
    """Provides a sample FinancialStatement object with typical data for testing."""
    return FinancialStatement(
        ticker="TEST",
        period="FY",
        fiscal_year=2023,
        end_date=datetime(2023, 12, 31),
        source_url="http://example.com",
        income_statement=IncomeStatement(
            revenue=1000,
            gross_profit=400,
            operating_income=200,
            net_income=100,
            interest_expense=20
        ),
        balance_sheet=BalanceSheet(
            current_assets=500,
            total_assets=2000,
            inventory=100,
            cash_and_equivalents=50,
            current_liabilities=250,
            total_liabilities=1000,
            total_debt=800,
            shareholders_equity=1000
        ),
        cash_flow_statement=CashFlowStatement(
            operating_cash_flow=180
        )
    )

def test_calculate_ratios_happy_path(sample_statement):
    """Tests that all ratios are calculated correctly with valid inputs."""
    ratios = CalculationService.calculate_ratios(sample_statement)

    assert ratios.ticker == "TEST"
    assert ratios.fiscal_year == 2023
    
    # Liquidity
    assert ratios.current_ratio == pytest.approx(500 / 250) # 2.0
    assert ratios.quick_ratio == pytest.approx((500 - 100) / 250) # 1.6
    assert ratios.cash_ratio == pytest.approx(50 / 250) # 0.2

    # Profitability
    assert ratios.net_margin == pytest.approx(100 / 1000) # 0.1
    assert ratios.gross_margin == pytest.approx(400 / 1000) # 0.4
    assert ratios.roe == pytest.approx(100 / 1000) # 0.1
    assert ratios.roa == pytest.approx(100 / 2000) # 0.05

    # Leverage
    assert ratios.debt_to_equity == pytest.approx(800 / 1000) # 0.8
    assert ratios.times_interest_earned == pytest.approx(200 / 20) # 10.0

def test_calculate_ratios_with_zero_denominator(sample_statement):
    """Tests that calculations return None when a denominator is zero."""
    # Modify statement to create division-by-zero scenarios
    sample_statement.income_statement.revenue = 0
    sample_statement.balance_sheet.current_liabilities = 0

    ratios = CalculationService.calculate_ratios(sample_statement)

    assert ratios.net_margin is None
    assert ratios.current_ratio is None
    
def test_calculate_ratios_with_none_input(sample_statement):
    """Tests that calculations return None when a required input is None."""
    # Modify statement to have missing data
    sample_statement.income_statement.revenue = None
    sample_statement.balance_sheet.current_liabilities = 250 # Reset this
    sample_statement.balance_sheet.current_assets = None

    ratios = CalculationService.calculate_ratios(sample_statement)

    assert ratios.net_margin is None
    assert ratios.current_ratio is None

def test_safe_divide_logic():
    """Directly tests the _safe_divide helper function."""
    assert CalculationService._safe_divide(10, 2) == 5
    assert CalculationService._safe_divide(10, 0) is None
    assert CalculationService._safe_divide(None, 2) is None
    assert CalculationService._safe_divide(10, None) is None
    assert CalculationService._safe_divide(None, None) is None
