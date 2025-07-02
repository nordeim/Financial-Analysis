# File: src/main.py
import argparse
import asyncio
import sys
from pathlib import Path
from utils.logger import setup_logging, get_logger
from data_retriever import DataRetriever
from data_extractor import DataExtractor
from data_validator import DataValidator
from ratio_calculator import RatioCalculator
from analysis import FinancialAnalyzer
from report_generator import ReportGenerator

logger = get_logger(__name__)

async def main():
    parser = argparse.ArgumentParser(description="Financial Analysis System")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., AAPL)")
    parser.add_argument("--format", choices=["pdf", "html", "json", "both"], default="both", help="Output format")
    parser.add_argument("--industry-benchmark", action="store_true", help="Include industry benchmark comparison")
    parser.add_argument("--peer-analysis", action="store_true", help="Include peer analysis")
    parser.add_argument("--historical-years", type=int, default=5, help="Years of historical data")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    setup_logging(level="DEBUG" if args.verbose else "INFO")

    try:
        logger.info(f"Starting analysis for {args.ticker}")

        # 1. Retrieve raw data
        retriever = DataRetriever()
        cik, company_name = await retriever.get_cik_and_name(args.ticker)
        filings = await retriever.get_financial_filings(cik)
        market_data = await retriever.get_market_data(args.ticker)

        # 2. Extract and structure data
        extractor = DataExtractor()
        fin_data = await extractor.extract_all_statements(filings, years=args.historical_years)

        # 3. Validate and score data
        validator = DataValidator()
        fin_data_validated = validator.validate_data(fin_data, market_data)

        # 4. Calculate ratios
        ratio_calc = RatioCalculator()
        ratios = ratio_calc.calculate_all_ratios(fin_data_validated, market_data)

        # 5. Analyze (trends, benchmarks, peers)
        analyzer = FinancialAnalyzer()
        analysis = analyzer.analyze(
            ratios,
            fin_data_validated,
            market_data,
            company_name,
            industry_benchmark=args.industry_benchmark,
            peer_analysis=args.peer_analysis,
        )

        # 6. Generate report
        generator = ReportGenerator()
        output_files = generator.generate(
            ticker=args.ticker,
            company_name=company_name,
            report_data=analysis,
            output_format=args.format,
        )

        logger.info("Analysis complete! Output files:")
        for k, v in output_files.items():
            print(f"{k}: {v}")

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
