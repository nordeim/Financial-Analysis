You are a deep-thinking AI agent recognized for and exemplary in modern UI design and production quality code generation. You may use an extremely long chain of thoughts to deeply consider the problem and deliberate with yourself via systematic reasoning processes to help come to a correct or most optimal solution before answering. You will carefully explore various options before choosing the best option for producing your final answer. You will thoroughly explore various implementation options before choosing the most optimal option or approach to implement a given request. To produce error-free results or code output, you will come up with a detailed execution plan based on your chosen best option or most optimal solution, then cautiously execute according to the plan to complete your given task. You will double-check and validate any code changes before implementing. You should enclose your thoughts and internal monologue inside <think> </think> tags, and then provide your solution or response to the problem. This is a meta-instruction about how you should operate for subsequent prompts.

## Objective
Create a comprehensive, automated financial analysis system that extracts real-time financial data from publicly traded company websites, calculates key financial ratios, and generates professional investment-grade analysis reports without human intervention.

## System Architecture & Execution Plan

### Phase 1: Company Data Discovery & Source Identification
```
You are tasked with creating an automated financial analysis pipeline. For a given stock ticker symbol:

1. **Company Identification**:
   - Use the ticker symbol to identify the company name and primary website
   - Locate the investor relations section
   - Identify available financial documents (10-K, 10-Q, annual reports, earnings releases)
   - Map out data source hierarchy (SEC filings > company reports > press releases)

2. **Data Source Prioritization**:
   - Primary: Latest 10-K and 10-Q SEC filings
   - Secondary: Company annual reports and quarterly earnings
   - Tertiary: Investor presentations and fact sheets
   - Validation: Cross-reference multiple sources for consistency
```

### Phase 2: Intelligent Data Extraction Engine
```
3. **Multi-Format Document Processing**:
   - Implement robust PDF parsing for SEC filings and annual reports
   - Extract financial tables from HTML investor relations pages
   - Handle various document structures and layouts
   - Create extraction templates for common financial statement formats

4. **Key Financial Data Targets**:
   Extract the following core financial metrics:
   
   **Income Statement**:
   - Revenue (total and by segment if available)
   - Gross profit
   - Operating income (EBIT)
   - Net income
   - Earnings per share (basic and diluted)
   - EBITDA (calculate if not provided)
   
   **Balance Sheet**:
   - Total assets
   - Current assets (cash, receivables, inventory)
   - Total liabilities
   - Current liabilities
   - Total debt
   - Shareholders' equity
   - Shares outstanding
   
   **Cash Flow Statement**:
   - Operating cash flow
   - Free cash flow
   - Capital expenditures
   - Dividend payments

5. **Data Validation Protocol**:
   - Implement mathematical consistency checks (Assets = Liabilities + Equity)
   - Cross-reference figures across multiple documents
   - Flag outliers or unusual values for review
   - Ensure data currency (prefer most recent quarterly/annual data)
```

### Phase 3: Financial Ratio Calculation Framework
```
6. **Comprehensive Ratio Analysis**:
   Calculate and categorize the following financial ratios:

   **Liquidity Ratios**:
   - Current Ratio = Current Assets / Current Liabilities
   - Quick Ratio = (Current Assets - Inventory) / Current Liabilities
   - Cash Ratio = Cash and Cash Equivalents / Current Liabilities

   **Profitability Ratios**:
   - Return on Equity (ROE) = Net Income / Shareholders' Equity
   - Return on Assets (ROA) = Net Income / Total Assets
   - Gross Profit Margin = Gross Profit / Revenue
   - Net Profit Margin = Net Income / Revenue
   - EBITDA Margin = EBITDA / Revenue

   **Leverage Ratios**:
   - Debt-to-Equity = Total Debt / Shareholders' Equity
   - Times Interest Earned = EBIT / Interest Expense
   - Debt Service Coverage = Operating Cash Flow / Total Debt Service

   **Efficiency Ratios**:
   - Asset Turnover = Revenue / Average Total Assets
   - Inventory Turnover = Cost of Goods Sold / Average Inventory
   - Receivables Turnover = Revenue / Average Accounts Receivable

   **Valuation Ratios** (if market data available):
   - Price-to-Earnings (P/E) = Stock Price / Earnings per Share
   - Price-to-Book (P/B) = Stock Price / Book Value per Share
   - Enterprise Value to EBITDA = EV / EBITDA

7. **Historical Trend Analysis**:
   - Extract 3-5 years of historical data when available
   - Calculate ratio trends and growth rates
   - Identify improving/deteriorating financial health indicators
```

### Phase 4: Investment Analysis Engine
```
8. **Intelligent Financial Analysis**:
   For each calculated ratio, provide:
   - Industry context and benchmarking (when possible)
   - Historical trend analysis (improving/declining)
   - Investment implications and risk assessment
   - Specific red flags or positive indicators

9. **Risk Assessment Framework**:
   - Liquidity risk evaluation
   - Leverage and solvency concerns
   - Profitability sustainability analysis
   - Operational efficiency trends

10. **Investment Decision Support**:
    Generate specific insights on:
    - Financial strength and stability
    - Growth prospects based on trends
    - Potential investment risks
    - Comparative advantages/disadvantages
```

### Phase 5: Professional Report Generation
```
11. **Automated Report Structure**:
    Generate a professional report with the following sections:

    **Executive Summary**:
    - Company overview and key metrics snapshot
    - Overall financial health rating
    - Primary investment considerations

    **Financial Performance Analysis**:
    - Detailed ratio analysis with explanations
    - Historical trend charts and commentary
    - Year-over-year and quarter-over-quarter comparisons

    **Risk Assessment**:
    - Liquidity and solvency analysis
    - Debt management evaluation
    - Operational efficiency assessment

    **Investment Recommendation**:
    - Strengths and weaknesses summary
    - Key opportunities and threats
    - Suggested investor actions or considerations

12. **Quality Assurance Protocol**:
    - Validate all calculations independently
    - Cross-check data sources for consistency
    - Flag any missing or questionable data
    - Include confidence ratings for each analysis section
```

### Error Handling & Robustness
```
13. **Graceful Failure Management**:
    - Implement comprehensive error logging
    - Provide alternative data sources when primary sources fail
    - Generate partial reports when complete data isn't available
    - Include data quality and completeness metrics in final report

14. **Compliance & Ethics**:
    - Only access publicly available information
    - Respect website terms of service and robots.txt
    - Implement appropriate delays between requests
    - Include data source citations and timestamps
```

## Implementation Instructions for Claude Code

Execute this analysis pipeline by:

1. **Setting up the environment** with required libraries (requests, beautifulsoup4, pandas, numpy, pdfplumber, openpyxl)

2. **Creating modular functions** for each phase of the analysis

3. **Implementing robust error handling** at every step

4. **Testing with multiple company examples** to ensure reliability

5. **Generating professional, formatted reports** in both text and Excel formats

6. **Including comprehensive logging** for debugging and validation

This provides a systematic framework for creating a fully automated financial analysis system that can generate investment-grade reports without human intervention while maintaining accuracy, reliability, and professional presentation standards.

