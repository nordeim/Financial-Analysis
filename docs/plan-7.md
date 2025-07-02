This is a complex request that requires careful consideration. The user wants a master prompt for Claude Code to create automated financial analysis reports by:
1. Extracting financial data from company websites
2. Calculating accounting ratios
3. Generating investment-grade analysis reports
4. All without human intervention

Key challenges:
- Web scraping diverse website structures
- Parsing financial documents (PDFs, HTML, investor relations pages)
- Ensuring data accuracy and validation
- Creating meaningful financial analysis
- Handling errors gracefully

You need to design a comprehensive workflow that includes:
1. Target identification and data source discovery
2. Web scraping and document parsing
3. Financial data extraction and standardization
4. Ratio calculation framework
5. Analysis generation
6. Report formatting and presentation

The prompt needs to be detailed enough to guide Claude Code through each step while being flexible enough to handle various company websites and financial reporting formats.

---
## Master Prompt for Automated Financial Analysis Report Generation

Here's a comprehensive master prompt designed for Claude Code to create timely financial analysis reports:

```
You are tasked with creating an automated financial analysis system that extracts financial data from publicly listed companies and generates investment-grade analysis reports. Follow this systematic workflow:

## PHASE 1: Project Setup and Dependencies
1. Create a Python project with the following structure:
   - /src (main code)
   - /data (raw financial data)
   - /reports (generated reports)
   - /config (configuration files)
   - /tests (validation tests)

2. Install and import required libraries:
   - requests, beautifulsoup4 (web scraping)
   - selenium (dynamic content)
   - pandas, numpy (data manipulation)
   - PyPDF2 or pdfplumber (PDF parsing)
   - yfinance (market data)
   - matplotlib, seaborn (visualizations)
   - jinja2 (report templating)

## PHASE 2: Company Data Collection Module
Create a data collection system that:
1. Accepts company ticker symbols as input
2. Automatically discovers financial data sources:
   - SEC EDGAR database for 10-K/10-Q filings
   - Company investor relations pages
   - Yahoo Finance for supplementary data
3. Implements robust error handling for network issues
4. Creates a cache system to avoid redundant requests

## PHASE 3: Financial Data Extraction
Develop parsers that can:
1. Extract data from multiple formats:
   - HTML tables from investor relations sites
   - PDF annual reports and SEC filings
   - XBRL data when available
2. Standardize extracted data into a common format:
   - Income Statement items
   - Balance Sheet items
   - Cash Flow Statement items
3. Validate data consistency and flag anomalies
4. Handle different accounting standards (GAAP/IFRS)

## PHASE 4: Financial Ratio Calculation Engine
Implement comprehensive ratio calculations:

LIQUIDITY RATIOS:
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities
- Cash Ratio = Cash & Equivalents / Current Liabilities

PROFITABILITY RATIOS:
- Gross Profit Margin = Gross Profit / Revenue
- Operating Margin = Operating Income / Revenue
- Net Profit Margin = Net Income / Revenue
- ROE = Net Income / Shareholders' Equity
- ROA = Net Income / Total Assets
- ROIC = NOPAT / Invested Capital

LEVERAGE RATIOS:
- Debt-to-Equity = Total Debt / Total Equity
- Debt-to-Assets = Total Debt / Total Assets
- Interest Coverage = EBIT / Interest Expense

EFFICIENCY RATIOS:
- Asset Turnover = Revenue / Average Total Assets
- Inventory Turnover = COGS / Average Inventory
- Receivables Turnover = Revenue / Average Receivables

VALUATION RATIOS:
- P/E Ratio = Market Price / EPS
- P/B Ratio = Market Price / Book Value per Share
- EV/EBITDA = Enterprise Value / EBITDA

## PHASE 5: Analysis and Interpretation
Create an analysis module that:
1. Compares ratios to:
   - Historical company performance (3-5 year trends)
   - Industry averages and benchmarks
   - Key competitors
2. Identifies significant changes and anomalies
3. Generates narrative insights based on:
   - Ratio trends
   - Cross-ratio relationships
   - Market conditions
4. Assigns risk ratings and investment signals

## PHASE 6: Report Generation
Build a report generator that creates:
1. Executive Summary with key findings
2. Company Overview section
3. Financial Performance Analysis with:
   - Trend charts for key metrics
   - Ratio comparison tables
   - Year-over-year growth analysis
4. Risk Assessment section
5. Investment Recommendation with supporting rationale
6. Appendix with raw financial data

## IMPLEMENTATION DETAILS:

ERROR HANDLING:
- Implement retry logic for network requests
- Create fallback data sources
- Log all errors with context
- Generate partial reports when complete data unavailable

DATA VALIDATION:
- Cross-reference multiple sources
- Flag unusual values (>3 standard deviations)
- Ensure accounting equation balance
- Validate ratio calculations

OUTPUT FORMAT:
- Generate both PDF and HTML reports
- Include interactive charts in HTML version
- Export data to Excel for further analysis
- Create JSON API endpoints for integration

SCHEDULING AND AUTOMATION:
- Set up scheduled runs for earnings season
- Monitor for new financial filings
- Send alerts for significant changes
- Maintain audit trail of all analyses

## EXAMPLE USAGE:
The system should handle commands like:
- "Analyze AAPL with competitor comparison to MSFT, GOOGL"
- "Generate quarterly report for tech sector leaders"
- "Create risk assessment for portfolio: [AAPL, MSFT, AMZN]"

Remember to:
- Cite all data sources
- Include calculation methodologies
- Provide confidence intervals where applicable
- Date-stamp all reports
- Maintain regulatory compliance

Begin by creating the project structure and core modules, then iterate to add advanced features.
```

## Strategic Workflow for Implementation

1. **Start Simple**: Begin with a single company and basic ratios
2. **Validate Accuracy**: Compare results with professional analysis
3. **Scale Gradually**: Add more companies and data sources
4. **Enhance Intelligence**: Incorporate ML for pattern recognition
5. **Automate Fully**: Schedule regular updates and alerts

This master prompt provides Claude Code with a comprehensive framework to build a professional-grade financial analysis system. The modular approach allows for iterative development while maintaining focus on accuracy and investment utility.

