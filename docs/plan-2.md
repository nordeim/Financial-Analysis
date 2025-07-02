<think>
This is a sophisticated request that requires deep consideration of multiple complex factors. Let me systematically think through the optimal approach for creating an automated financial analysis system.

**Core Challenge Analysis:**
1. **Data Source Strategy**: Direct website scraping is unreliable and potentially problematic due to anti-bot measures, varying website structures, and legal concerns. A better approach would be to use standardized financial data sources.

2. **Data Reliability**: Financial data accuracy is critical for investment decisions, so the system needs robust validation mechanisms.

3. **Automation Workflow**: The system needs to handle the entire pipeline from data acquisition to report generation with minimal human intervention.

4. **Financial Analysis Depth**: The system should calculate meaningful ratios and provide contextual analysis, not just raw numbers.

**Optimal Implementation Strategy:**
Rather than scraping company websites directly, I should design a system that leverages:
- SEC EDGAR database for US public companies (standardized filings)
- Company investor relations pages (which typically have standardized sections)
- Financial data APIs where appropriate
- Structured financial statements (10-K, 10-Q forms)

**Key Components Needed:**
1. Company identification and data source mapping
2. Automated data extraction with validation
3. Financial ratio calculation engine
4. Trend analysis and benchmarking
5. Professional report generation
6. Quality assurance and error handling

**Technical Architecture:**
The solution should be modular, with clear separation of concerns:
- Data acquisition module
- Data processing and validation module
- Financial analysis engine
- Report generation module
- Error handling and logging system

Let me now craft a comprehensive master prompt that addresses all these considerations while being practical and implementable.
</think>

# Master Prompt for Automated Financial Analysis System

## Overview
Create a comprehensive automated financial analysis system that extracts financial data from reliable sources, calculates key financial ratios, and generates professional investment-grade reports without human intervention.

## System Architecture & Workflow

### Phase 1: Data Source Strategy & Acquisition
```
Create a multi-source data acquisition system with the following priority hierarchy:

PRIMARY SOURCES:
1. SEC EDGAR database (for US public companies)
   - Access 10-K, 10-Q, and 8-K filings via SEC API
   - Parse XBRL formatted financial statements
   - Extract: Income Statement, Balance Sheet, Cash Flow Statement

2. Company Investor Relations Pages
   - Target standardized IR sections: /investor-relations/, /investors/
   - Look for quarterly/annual earnings releases
   - Extract earnings presentations and financial fact sheets

3. Financial Data APIs (fallback)
   - Yahoo Finance API for market data
   - Alpha Vantage for fundamental data
   - Validate against primary sources

IMPLEMENTATION REQUIREMENTS:
- Implement respectful scraping (rate limiting: 1 request/second minimum)
- Follow robots.txt protocols
- Use proper User-Agent headers
- Implement exponential backoff for failed requests
- Log all data sources and timestamps for audit trail
```

### Phase 2: Data Extraction & Validation Engine
```
Build a robust data extraction system with multi-layer validation:

EXTRACTION TARGETS:
Financial Statement Items:
- Revenue/Sales
- Cost of Goods Sold
- Operating Income/EBIT
- Net Income
- Total Assets
- Current Assets (Cash, Inventory, Receivables)
- Total Liabilities
- Current Liabilities
- Shareholders' Equity
- Operating Cash Flow
- Free Cash Flow
- Shares Outstanding

VALIDATION FRAMEWORK:
1. Cross-source verification (compare data across sources)
2. Mathematical consistency checks (Balance Sheet equation, etc.)
3. Temporal consistency (reasonable period-over-period changes)
4. Industry benchmark validation
5. Outlier detection and flagging

ERROR HANDLING:
- Graceful degradation when data is unavailable
- Clear logging of missing or inconsistent data
- Fallback to previous periods when current data unavailable
- Quality scoring for each data point (High/Medium/Low confidence)
```

### Phase 3: Financial Ratio Calculation Engine
```
Implement comprehensive financial ratio analysis with the following categories:

LIQUIDITY RATIOS:
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities
- Cash Ratio = Cash & Cash Equivalents / Current Liabilities
- Operating Cash Flow Ratio = Operating Cash Flow / Current Liabilities

PROFITABILITY RATIOS:
- Gross Profit Margin = (Revenue - COGS) / Revenue
- Operating Margin = Operating Income / Revenue
- Net Profit Margin = Net Income / Revenue
- Return on Assets (ROA) = Net Income / Total Assets
- Return on Equity (ROE) = Net Income / Shareholders' Equity
- Return on Invested Capital (ROIC) = NOPAT / Invested Capital

LEVERAGE RATIOS:
- Debt-to-Equity = Total Debt / Shareholders' Equity
- Debt-to-Assets = Total Debt / Total Assets
- Interest Coverage = EBIT / Interest Expense
- Debt Service Coverage = Operating Cash Flow / Total Debt Service

EFFICIENCY RATIOS:
- Asset Turnover = Revenue / Average Total Assets
- Inventory Turnover = COGS / Average Inventory
- Receivables Turnover = Revenue / Average Accounts Receivable
- Days Sales Outstanding = 365 / Receivables Turnover

VALUATION RATIOS (require market data):
- Price-to-Earnings (P/E) = Stock Price / EPS
- Price-to-Book (P/B) = Stock Price / Book Value per Share
- Enterprise Value / EBITDA
- Price/Sales Ratio

CALCULATION REQUIREMENTS:
- Use trailing twelve months (TTM) data where appropriate
- Calculate 3-year and 5-year averages for trend analysis
- Implement industry-specific ratio adjustments
- Handle edge cases (negative values, zero denominators)
- Provide confidence intervals for calculated ratios
```

### Phase 4: Analysis & Benchmarking Module
```
Create intelligent analysis layer that provides context and insights:

TREND ANALYSIS:
- Calculate year-over-year growth rates for all key metrics
- Identify improving/deteriorating trends over 3-5 year periods
- Detect inflection points and significant changes
- Seasonal adjustment for quarterly data

INDUSTRY BENCHMARKING:
- Compare ratios against industry medians and quartiles
- Identify peer companies for comparative analysis
- Flag ratios that are significantly above/below industry norms
- Provide industry context for ratio interpretation

QUALITY SCORING:
- Financial strength score (1-10 scale)
- Profitability trend score
- Liquidity adequacy assessment
- Leverage risk evaluation
- Overall investment attractiveness rating

RED FLAG DETECTION:
- Deteriorating working capital trends
- Unsustainable debt levels
- Declining profitability patterns
- Cash flow vs. earnings discrepancies
- Going concern indicators
```

### Phase 5: Professional Report Generation
```
Generate comprehensive, investment-grade reports with the following structure:

EXECUTIVE SUMMARY:
- Company overview and business model
- Key financial highlights
- Overall investment thesis (3-4 sentences)
- Risk assessment summary

FINANCIAL PERFORMANCE ANALYSIS:
- Revenue and profitability trends
- Margin analysis and drivers
- Cash flow analysis
- Balance sheet strength assessment

RATIO ANALYSIS DASHBOARD:
- Visual ratio comparison vs. industry
- Historical trend charts (5-year)
- Peer comparison tables
- Red flag indicators

VALUATION ASSESSMENT:
- Current valuation metrics
- Historical valuation ranges
- Peer valuation comparison
- Fair value estimate range

RISK ANALYSIS:
- Financial risks identified
- Industry-specific risks
- Liquidity and solvency assessment
- Key ratio deterioration alerts

INVESTMENT RECOMMENDATION:
- Strengths and weaknesses summary
- Catalysts and concerns
- Target price range (if applicable)
- Investment time horizon considerations

FORMATTING REQUIREMENTS:
- Professional PDF output with charts and tables
- Executive summary on first page
- Detailed appendix with all calculated ratios
- Data source attribution and timestamps
- Confidence levels for all major conclusions
```

### Phase 6: Quality Assurance & Monitoring
```
Implement comprehensive QA system:

DATA QUALITY CHECKS:
- Automated validation of all financial statement relationships
- Cross-reference calculations with multiple sources
- Flag unusual ratio movements for manual review
- Maintain data lineage for all calculations

REPORT QUALITY ASSURANCE:
- Spell check and grammar validation
- Numerical accuracy verification
- Chart and table formatting consistency
- Ensure all sections are populated with relevant data

MONITORING & ALERTS:
- Daily data freshness checks
- Error rate monitoring and alerting
- Performance metrics tracking
- Automated system health reports

AUDIT TRAIL:
- Complete logging of data sources used
- Calculation methodology documentation
- Version control for report generation
- Timestamp all data extraction and processing steps
```

### Implementation Command Structure
```
Execute this system with the following command pattern:

python financial_analyzer.py --company [TICKER] --period [quarterly/annual] --depth [basic/comprehensive] --output [pdf/json/both]

Optional flags:
--industry-benchmark [enable industry comparison]
--peer-analysis [include peer comparison]
--historical-years [1-10, default 5]
--confidence-threshold [high/medium/low]
--update-frequency [daily/weekly/monthly]
```

This master prompt creates a robust, professional-grade financial analysis system that can operate autonomously while maintaining high standards of accuracy and reliability. The modular design allows for easy maintenance and enhancement, while the comprehensive error handling ensures reliable operation even when data sources are temporarily unavailable.
