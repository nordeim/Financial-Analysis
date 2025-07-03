# File: src/financial_analysis/services/analysis_service.py
# Purpose: Generates qualitative analysis from quantitative ratio data.

import logging
from typing import List, Dict, Any, Optional

from ..core.models import FinancialRatios

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Generates qualitative, data-driven analysis from historical financial ratios.
    This service translates quantitative data into objective, human-readable insights.
    """

    def _get_trend(self, data: List[Optional[float]]) -> str:
        """Determines the trend from a list of historical data points."""
        # Filter out None values for trend calculation
        valid_data = [d for d in data if d is not None]
        if len(valid_data) < 2:
            return "stable (insufficient data)"
        
        if valid_data[0] > valid_data[-1]:
            return "improving"
        elif valid_data[0] < valid_data[-1]:
            return "declining"
        else:
            return "stable"

    def _analyze_liquidity(self, ratios: List[FinancialRatios]) -> str:
        """Analyzes liquidity position."""
        latest = ratios[0]
        if latest.current_ratio is None:
            return "Liquidity data is not available."

        historical_cr = [r.current_ratio for r in ratios]
        trend = self._get_trend(historical_cr)
        
        text = f"The most recent Current Ratio is {latest.current_ratio:.2f}, showing a {trend} trend. "
        
        if latest.current_ratio >= 2.0:
            text += "This indicates a very strong ability to meet short-term obligations."
        elif latest.current_ratio >= 1.5:
            text += "This suggests a healthy liquidity position."
        elif latest.current_ratio >= 1.0:
            text += "This indicates an adequate but potentially tight liquidity position."
        else:
            text += "This is below 1.0, signaling potential risk in meeting short-term liabilities."
        return text

    def _analyze_profitability(self, ratios: List[FinancialRatios]) -> str:
        """Analyzes profitability metrics."""
        latest = ratios[0]
        if latest.net_margin is None or latest.roe is None:
            return "Profitability data is not available."
            
        historical_nm = [r.net_margin for r in ratios]
        trend = self._get_trend(historical_nm)

        text = (f"The company's latest Net Profit Margin is {latest.net_margin:.2%}, "
                f"with a {trend} trend over the analyzed period. "
                f"Return on Equity (ROE) stands at {latest.roe:.2%}. ")

        if latest.net_margin >= 0.15:
            text += "This indicates excellent profitability and strong operational efficiency."
        elif latest.net_margin >= 0.05:
            text += "This reflects solid profitability."
        elif latest.net_margin > 0:
            text += "Profitability is positive but margins are thin, suggesting competitive pressure or high costs."
        else:
            text += "The company is operating at a net loss, which is a significant concern."
        return text

    def _analyze_leverage(self, ratios: List[FinancialRatios]) -> str:
        """Analyzes debt and leverage position."""
        latest = ratios[0]
        if latest.debt_to_equity is None:
            return "Leverage data is not available."

        historical_de = [r.debt_to_equity for r in ratios]
        trend = self._get_trend(historical_de) # Note: For D/E, "improving" means it's going down.
        
        text = (f"The Debt-to-Equity ratio is {latest.debt_to_equity:.2f}. "
                f"The trend is {trend}, where a declining number is generally favorable. ")
                
        if latest.debt_to_equity <= 0.4:
            text += "This indicates a conservative and strong balance sheet with low reliance on debt."
        elif latest.debt_to_equity <= 1.0:
            text += "This suggests a moderate and generally acceptable level of debt."
        elif latest.debt_to_equity <= 2.0:
            text += "This indicates an elevated level of debt, increasing financial risk."
        else:
            text += "This represents a high level of debt, which may pose significant financial risk."
        return text
        
    def _analyze_efficiency(self, ratios: List[FinancialRatios]) -> str:
        """Analyzes operational efficiency."""
        latest = ratios[0]
        if latest.asset_turnover is None:
            return "Efficiency data is not available."
            
        historical_at = [r.asset_turnover for r in ratios]
        trend = self._get_trend(historical_at)

        text = (f"Asset Turnover ratio is {latest.asset_turnover:.2f}, with a {trend} trend. "
                "This ratio measures how efficiently the company uses its assets to generate revenue. ")
                
        if latest.asset_turnover >= 1.0:
            text += "A ratio above 1.0 suggests efficient use of assets."
        elif latest.asset_turnover >= 0.5:
            text += "This suggests a moderate level of asset efficiency."
        else:
            text += "A low ratio may indicate underutilization of assets or an asset-heavy business model."
        return text
    
    def _synthesize_findings(self, analysis: Dict[str, str], ratios: List[FinancialRatios]) -> Dict[str, Any]:
        """Creates a high-level summary of strengths and weaknesses."""
        latest = ratios[0]
        strengths = []
        concerns = []

        # Liquidity
        if latest.current_ratio and latest.current_ratio >= 1.5:
            strengths.append(f"Strong liquidity ({analysis.get('liquidity', '')})")
        elif latest.current_ratio and latest.current_ratio < 1.0:
            concerns.append(f"Potential liquidity risk ({analysis.get('liquidity', '')})")

        # Profitability
        if latest.net_margin and latest.net_margin >= 0.10:
            strengths.append(f"High profitability ({analysis.get('profitability', '')})")
        elif latest.net_margin and latest.net_margin < 0:
            concerns.append(f"Operating at a net loss ({analysis.get('profitability', '')})")

        # Leverage
        if latest.debt_to_equity and latest.debt_to_equity <= 0.5:
            strengths.append(f"Low financial leverage ({analysis.get('leverage', '')})")
        elif latest.debt_to_equity and latest.debt_to_equity > 1.5:
            concerns.append(f"High debt levels ({analysis.get('leverage', '')})")

        overall = "The company presents a mixed financial profile."
        if len(strengths) > len(concerns) and not concerns:
            overall = "The company demonstrates a strong overall financial position based on the available data."
        elif len(concerns) > len(strengths):
            overall = "The analysis highlights several areas of concern that warrant attention."
        
        return {
            "key_strengths": strengths,
            "key_concerns": concerns,
            "overall_summary": overall
        }

    def generate_qualitative_analysis(self, historical_ratios: List[FinancialRatios]) -> Dict[str, Any]:
        """
        Generates a full qualitative analysis from a historical list of ratios.

        Args:
            historical_ratios: A list of FinancialRatios, sorted from most recent to oldest.

        Returns:
            A dictionary containing textual analysis for each financial area.
        """
        if not historical_ratios:
            logger.warning("Cannot generate analysis: historical ratios list is empty.")
            return {"error": "No ratio data available to analyze."}

        logger.info(f"Generating qualitative analysis for {historical_ratios[0].ticker}.")

        analysis = {
            "liquidity": self._analyze_liquidity(historical_ratios),
            "profitability": self._analyze_profitability(historical_ratios),
            "leverage": self._analyze_leverage(historical_ratios),
            "efficiency": self._analyze_efficiency(historical_ratios),
        }
        
        synthesis = self._synthesize_findings(analysis, historical_ratios)
        analysis.update(synthesis)
        
        return analysis
