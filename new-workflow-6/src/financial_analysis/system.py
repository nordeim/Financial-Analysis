# File: src/financial_analysis/system.py
# Purpose: Encapsulates the entire financial analysis workflow orchestration.

import logging
from datetime import datetime
from pathlib import Path

from .core.models import CompanyAnalysis
from .services.data_service import DataService
from .services.calculation_service import CalculationService
from .services.analysis_service import AnalysisService
from .reporting.base_reporter import BaseReporter

logger = logging.getLogger(__name__)

class FinancialAnalysisSystem:
    """
    Orchestrates the entire financial analysis pipeline, from data fetching
    to report generation.
    """
    def __init__(
        self,
        data_service: DataService,
        calculation_service: CalculationService,
        analysis_service: AnalysisService,
        reporters: list[BaseReporter]
    ):
        self.data_service = data_service
        self.calculation_service = calculation_service
        self.analysis_service = analysis_service
        self.reporters = reporters

    def run(self, ticker: str, num_years: int, output_dir: Path):
        """
        Executes the full analysis pipeline for a given company.

        Args:
            ticker: The stock ticker symbol to analyze.
            num_years: The number of historical years to analyze.
            output_dir: The directory to save the generated reports.
        """
        logger.info(f"--- Starting comprehensive analysis for {ticker} ---")
        
        # 1. Fetch Data
        company_info, statements = self.data_service.fetch_company_financials(ticker, num_years)

        if not statements:
            logger.error(f"No financial statements could be retrieved for {ticker}. Aborting.")
            return

        # 2. Calculate Ratios
        historical_ratios = [self.calculation_service.calculate_ratios(s) for s in statements]

        # 3. Generate Qualitative Analysis
        qualitative_analysis = self.analysis_service.generate_qualitative_analysis(historical_ratios)

        # 4. Assemble the final analysis object
        final_analysis = CompanyAnalysis(
            company_info=company_info,
            historical_statements=statements,
            historical_ratios=historical_ratios,
            qualitative_analysis=qualitative_analysis,
            data_sources_used=[p.__class__.__name__ for p in self.data_service.providers]
        )

        # 5. Generate Reports
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for reporter in self.reporters:
            reporter_name = reporter.__class__.__name__.replace("Reporter", "").lower()
            file_extension = "xlsx" if reporter_name == "excel" else "txt"
            output_path = output_dir / f"{ticker}_analysis_{timestamp}.{file_extension}"
            
            try:
                reporter.generate_report(final_analysis, str(output_path))
            except Exception as e:
                logger.error(f"Failed to generate report with {reporter.__class__.__name__}: {e}")

        logger.info(f"--- Analysis for {ticker} completed successfully. Reports are in {output_dir} ---")
