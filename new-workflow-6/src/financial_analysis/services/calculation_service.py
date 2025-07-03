# File: src/financial_analysis/services/calculation_service.py
# Purpose: Performs all financial ratio calculations.

import logging
from typing import Optional

from ..core.models import FinancialStatement, FinancialRatios

logger = logging.getLogger(__name__)

class CalculationService:
    """
    A stateless service responsible for calculating financial ratios
    from a given financial statement.
    """

    @staticmethod
    def _safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
        """
        Safely divides two numbers, handling None inputs and division by zero.

        Returns:
            The result of the division, or None if the calculation is not possible.
        """
        if numerator is None or denominator is None or denominator == 0:
            return None
        return numerator / denominator

    @staticmethod
    def calculate_ratios(statement: FinancialStatement) -> FinancialRatios:
        """
        Calculates a comprehensive set of financial ratios for a single period.

        Args:
            statement: A FinancialStatement object containing the raw data.

        Returns:
            A FinancialRatios object populated with the calculated ratios.
        """
        logger.info(f"Calculating ratios for {statement.ticker} for FY{statement.fiscal_year}.")
        
        i = statement.income_statement
        b = statement.balance_sheet
        c = statement.cash_flow_statement
        
        # --- Liquidity Ratios ---
        current_ratio = CalculationService._safe_divide(b.current_assets, b.current_liabilities)
        
        quick_assets = None
        if b.current_assets is not None and b.inventory is not None:
            quick_assets = b.current_assets - b.inventory
        quick_ratio = CalculationService._safe_divide(quick_assets, b.current_liabilities)
        
        cash_ratio = CalculationService._safe_divide(b.cash_and_equivalents, b.current_liabilities)

        # --- Profitability Ratios ---
        roe = CalculationService._safe_divide(i.net_income, b.shareholders_equity)
        roa = CalculationService._safe_divide(i.net_income, b.total_assets)
        gross_margin = CalculationService._safe_divide(i.gross_profit, i.revenue)
        net_margin = CalculationService._safe_divide(i.net_income, i.revenue)
        ebitda_margin = CalculationService._safe_divide(i.ebitda, i.revenue)

        # --- Leverage Ratios ---
        debt_to_equity = CalculationService._safe_divide(b.total_debt, b.shareholders_equity)
        debt_to_assets = CalculationService._safe_divide(b.total_debt, b.total_assets)
        times_interest_earned = CalculationService._safe_divide(i.operating_income, i.interest_expense)
        
        debt_service_coverage = None
        if c.operating_cash_flow is not None and b.total_debt is not None:
            # Simplified DSCR - a more accurate version would use scheduled debt payments.
            debt_service_coverage = CalculationService._safe_divide(c.operating_cash_flow, b.total_debt)

        # --- Efficiency Ratios ---
        # Note: Proper turnover ratios use average balance sheet figures.
        # This is a simplification using year-end figures. A future enhancement could average balances.
        asset_turnover = CalculationService._safe_divide(i.revenue, b.total_assets)
        inventory_turnover = CalculationService._safe_divide(i.cost_of_goods_sold, b.inventory)
        receivables_turnover = CalculationService._safe_divide(i.revenue, b.accounts_receivable)
        
        return FinancialRatios(
            ticker=statement.ticker,
            period=statement.period,
            fiscal_year=statement.fiscal_year,
            # Liquidity
            current_ratio=current_ratio,
            quick_ratio=quick_ratio,
            cash_ratio=cash_ratio,
            # Profitability
            roe=roe,
            roa=roa,
            gross_margin=gross_margin,
            net_margin=net_margin,
            ebitda_margin=ebitda_margin,
            # Leverage
            debt_to_equity=debt_to_equity,
            debt_to_assets=debt_to_assets,
            times_interest_earned=times_interest_earned,
            debt_service_coverage=debt_service_coverage,
            # Efficiency
            asset_turnover=asset_turnover,
            inventory_turnover=inventory_turnover,
            receivables_turnover=receivables_turnover,
        )
