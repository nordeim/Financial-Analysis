# File: main.py
# Purpose: The main command-line entry point for the Financial Analysis System.

import argparse
import logging
import sys
from pathlib import Path

# Setup sys.path to allow imports from the 'src' directory
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from financial_analysis.core.logging_config import setup_logging
from financial_analysis.core.config import settings
from financial_analysis.system import FinancialAnalysisSystem
from financial_analysis.services.data_service import DataService
from financial_analysis.services.calculation_service import CalculationService
from financial_analysis.services.analysis_service import AnalysisService
from financial_analysis.data_providers.sec_edgar_provider import SecEdgarProvider
from financial_analysis.reporting.text_reporter import TextReporter
from financial_analysis.reporting.excel_reporter import ExcelReporter

# Initialize logging as the first action
setup_logging()
logger = logging.getLogger(__name__)

def main():
    """
    Main function to parse arguments and run the analysis system.
    """
    parser = argparse.ArgumentParser(description=settings.PROJECT_NAME)
    parser.add_argument(
        "-t", "--ticker",
        type=str,
        required=True,
        help="The stock ticker symbol of the company to analyze (e.g., AAPL)."
    )
    parser.add_argument(
        "-y", "--years",
        type=int,
        default=settings.NUM_HISTORICAL_YEARS,
        help=f"The number of historical years to analyze (default: {settings.NUM_HISTORICAL_YEARS})."
    )
    args = parser.parse_args()

    try:
        # --- Dependency Injection Setup ---
        # 1. Instantiate Providers (add more providers here in the future)
        sec_provider = SecEdgarProvider()
        
        # 2. Instantiate Services
        data_service = DataService(providers=[sec_provider])
        calculation_service = CalculationService()
        analysis_service = AnalysisService()
        
        # 3. Instantiate Reporters
        text_reporter = TextReporter()
        excel_reporter = ExcelReporter()
        
        # 4. Instantiate the main system orchestrator
        system = FinancialAnalysisSystem(
            data_service=data_service,
            calculation_service=calculation_service,
            analysis_service=analysis_service,
            reporters=[text_reporter, excel_reporter]
        )
        
        # 5. Run the system
        system.run(ticker=args.ticker, num_years=args.years, output_dir=settings.REPORTS_DIR)

    except Exception as e:
        logger.critical(f"A critical error occurred in the analysis pipeline: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
