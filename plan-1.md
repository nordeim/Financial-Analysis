<think>
This is a sophisticated request about automating financial analysis through Claude Code. Let me think through this systematically:

1. Core Requirements:
- Extract financial data from public company websites
- Calculate accounting ratios automatically
- Generate investment-grade analysis reports
- Fully automated workflow without human intervention

2. Key Challenges:
- Website structures vary greatly between companies
- Financial data can be in different formats (PDFs, HTML, interactive charts)
- Need to identify the most recent and relevant financial statements
- Must ensure accuracy in calculations
- Should provide contextual analysis, not just numbers

3. Data Sources to Consider:
- SEC EDGAR database (10-K, 10-Q filings)
- Company investor relations pages
- Financial data APIs (if available)
- Earnings releases and presentations

4. Essential Financial Ratios:
- Liquidity: Current ratio, quick ratio, cash ratio
- Profitability: ROE, ROA, gross/operating/net margins
- Leverage: Debt-to-equity, interest coverage, debt service coverage
- Efficiency: Asset turnover, inventory turnover, receivables turnover
- Valuation: P/E, P/B, EV/EBITDA, PEG ratio
- Growth: Revenue CAGR, earnings growth, FCF growth

5. Report Structure:
- Executive summary with key insights
- Company overview and recent developments
- Financial performance analysis
- Ratio analysis with peer comparison
- Trend analysis (3-5 year historical)
- Investment thesis and risks
- Conclusion and recommendations

Let me craft a comprehensive master prompt and workflow strategy.
</think>

# Master Strategy for Automated Financial Analysis Report Generation

## Strategic Workflow Architecture

### Phase 1: Data Acquisition Framework
```
1. Primary Data Sources (in order of reliability):
   - SEC EDGAR API for standardized filings (10-K, 10-Q, 8-K)
   - Company investor relations JSON/XML feeds
   - Structured data from financial APIs (Yahoo Finance, Alpha Vantage)
   - HTML scraping as last resort

2. Data Extraction Protocol:
   - Prioritize XBRL format for accuracy
   - Parse financial tables using regex patterns
   - Implement checksums for data validation
   - Store raw data with timestamps for audit trail
```

### Phase 2: Master Prompt for Claude Code

```
You are tasked with creating a comprehensive financial analysis report for [COMPANY_TICKER]. Follow this systematic approach:

## 1. DATA COLLECTION PHASE

### Primary Sources:
- Access SEC EDGAR database for the most recent 10-K and last 4 quarters of 10-Q filings
- Extract data from URLs: https://www.sec.gov/edgar/browse/?CIK=[CIK]&owner=exclude
- Fallback to company investor relations: https://investors.[company].com/financials

### Required Financial Statements:
- Income Statement (3-5 years)
- Balance Sheet (3-5 years)
- Cash Flow Statement (3-5 years)
- Segment reporting if available

### Data Extraction Rules:
1. Use BeautifulSoup/Selenium for web scraping
2. Parse XBRL tags when available: {us-gaap:Assets, us-gaap:Revenues, etc.}
3. Implement error handling for missing data
4. Validate extracted numbers against reported totals

## 2. CALCULATION ENGINE

### Core Financial Ratios to Calculate:

#### Liquidity Analysis:
- Current Ratio = Current Assets / Current Liabilities
- Quick Ratio = (Current Assets - Inventory) / Current Liabilities
- Cash Ratio = (Cash + Marketable Securities) / Current Liabilities

#### Profitability Metrics:
- Gross Margin = (Revenue - COGS) / Revenue
- Operating Margin = Operating Income / Revenue
- Net Margin = Net Income / Revenue
- ROE = Net Income / Average Shareholders' Equity
- ROA = Net Income / Average Total Assets
- ROIC = NOPAT / (Total Debt + Total Equity)

#### Leverage Assessment:
- Debt-to-Equity = Total Debt / Total Equity
- Interest Coverage = EBIT / Interest Expense
- Debt Service Coverage = (Net Income + Depreciation) / (Principal + Interest)

#### Efficiency Indicators:
- Asset Turnover = Revenue / Average Total Assets
- Inventory Turnover = COGS / Average Inventory
- Receivables Turnover = Revenue / Average Accounts Receivable
- Days Sales Outstanding = 365 / Receivables Turnover

#### Valuation Multiples:
- P/E Ratio = Market Price / EPS
- P/B Ratio = Market Price / Book Value per Share
- EV/EBITDA = Enterprise Value / EBITDA
- PEG Ratio = P/E Ratio / Earnings Growth Rate

#### Growth Metrics:
- Revenue CAGR (3-5 years)
- EBITDA Growth Rate
- Free Cash Flow Growth
- Dividend Growth Rate (if applicable)

## 3. ANALYTICAL FRAMEWORK

### Trend Analysis:
- Calculate year-over-year changes for all key metrics
- Identify inflection points and anomalies
- Create visualizations using matplotlib/plotly

### Peer Comparison:
- Identify 3-5 industry peers based on SIC/NAICS codes
- Calculate industry average ratios
- Position company relative to peers

### DuPont Analysis:
ROE = Net Margin × Asset Turnover × Equity Multiplier

### Altman Z-Score (bankruptcy prediction):
Z = 1.2(Working Capital/Total Assets) + 1.4(Retained Earnings/Total Assets) + 
    3.3(EBIT/Total Assets) + 0.6(Market Value of Equity/Total Liabilities) + 
    1.0(Sales/Total Assets)

## 4. REPORT GENERATION

### Structure:
1. Executive Summary (1 page)
   - Investment thesis in 3 bullet points
   - Key strengths and risks
   - Target price/recommendation

2. Company Overview (1-2 pages)
   - Business model description
   - Competitive positioning
   - Recent strategic initiatives

3. Financial Performance Analysis (3-4 pages)
   - Revenue and profitability trends
   - Balance sheet strength
   - Cash flow analysis
   - Working capital management

4. Ratio Analysis Dashboard (2 pages)
   - Visual representation of all ratios
   - Historical trends (line charts)
   - Peer comparison (bar charts)
   - Traffic light system (green/yellow/red) for performance

5. Investment Risks and Opportunities (1-2 pages)
   - SWOT analysis based on financial data
   - Key risk factors from 10-K Item 1A
   - Growth catalysts

6. Valuation and Recommendation (1-2 pages)
   - DCF model summary
   - Relative valuation vs peers
   - Price target calculation
   - Buy/Hold/Sell recommendation with rationale

### Quality Checks:
- Verify all calculations sum correctly
- Check for data anomalies (>50% changes)
- Ensure all ratios are within reasonable bounds
- Cross-reference with at least one financial database

### Output Format:
- Generate PDF report with embedded charts
- Create Excel workbook with all calculations
- Produce JSON file with structured data
- Optional: Interactive HTML dashboard

## 5. ERROR HANDLING AND EDGE CASES

Handle these scenarios:
- Missing financial data: Use industry averages or note as "N/A"
- Negative equity: Adjust ROE calculation
- One-time items: Calculate adjusted metrics
- Different fiscal year ends: Align periods appropriately
- Foreign currency: Convert to USD using period-end rates

## 6. AUTOMATION TRIGGERS

Set up to run:
- Quarterly after earnings releases
- When significant price movements occur (>10%)
- On-demand via API endpoint
```

### Phase 3: Implementation Checklist

1. **Initial Setup**
   - Configure API keys for data sources
   - Set up database for historical data storage
   - Create template library for different industries

2. **Data Pipeline**
   - Build robust web scraping functions
   - Implement data validation layers
   - Create fallback mechanisms for failed extractions

3. **Calculation Module**
   - Develop modular ratio calculation functions
   - Build industry-specific adjustments
   - Implement rolling period calculations

4. **Analysis Engine**
   - Create statistical analysis functions
   - Build anomaly detection algorithms
   - Develop peer selection logic

5. **Report Generator**
   - Design professional report templates
   - Build chart generation functions
   - Create natural language generation for insights

### Phase 4: Continuous Improvement Protocol

```python
# Pseudocode for self-improving system
def analyze_report_accuracy():
    # Compare predictions with actual outcomes
    # Adjust weights and thresholds
    # Log successful patterns
    
def update_extraction_patterns():
    # Monitor extraction failures
    # Update regex patterns
    # Add new data sources

def enhance_analysis_framework():
    # Track which metrics best predict performance
    # Adjust report emphasis accordingly
    # Incorporate new financial metrics
```

## Key Success Factors

1. **Data Quality**: Implement multiple validation checks
2. **Calculation Accuracy**: Cross-verify with established sources
3. **Timeliness**: Automate triggers for real-time updates
4. **Actionability**: Focus on decision-driving insights
5. **Scalability**: Design for handling multiple companies simultaneously

This comprehensive framework provides Claude Code with the structure and detail needed to autonomously generate institutional-quality financial analysis reports. The modular design allows for customization based on specific industries or investment strategies while maintaining consistency and reliability.
