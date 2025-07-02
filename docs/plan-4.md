**Step 1: Understand the Goal and Constraints**

- The user wants a master prompt (for "Claude Code" or a similar coding AI) that will generate a Python application to automate financial analysis of publicly listed companies.
- The system should extract financial results (ideally from company websites or official sources), compute accounting ratios, and produce an investment-grade report—**all without human intervention**.
- The report should be timely, reliable, and useful for investment decisions.

**Step 2: Review and Learn from Prior Art**

The user has provided three thorough plans, each with different depth, detail, and focus. Key observations:
- All recommend an API-first approach (SEC EDGAR, Yahoo Finance, etc.), only scraping as a fallback.
- Each plan emphasizes modularity, error handling, and thorough validation.
- They all break down the process into stages: Data Acquisition → Extraction/Validation → Ratio Calculation → Analysis & Reporting.
- The most advanced plans (plan-2, plan-3) discuss cross-source validation, trend/peer/benchmarking, and even generative AI for narrative reporting.

**Step 3: Identify the Most Modern, Robust, and Scalable Approach**

- Use official APIs (SEC, Yahoo Finance, Alpha Vantage).
- Scrape only if APIs fail, and do so respectfully (rate limits, robots.txt, etc.).
- Extract, validate, and structure financial data (Income Statement, Balance Sheet, Cash Flow).
- Calculate a comprehensive set of financial ratios (liquidity, profitability, leverage, efficiency, valuation).
- Benchmark and analyze trends, peer group, and industry context.
- Generate a professional report using a generative LLM for narrative.
- Ensure auditability, logging, and error resilience.

**Step 4: Consider the Prompt’s Audience (Claude Code or Similar)**

- The prompt must be explicit, systematic, and modular.
- It should specify not just *what* to do, but *how* to do it, and in which files/code modules.
- The prompt should strongly encourage best practices: robust error handling, modularity, validation, and professional output.

**Step 5: Enumerate and Refine the Workflow**

A. **Input:** Company stock ticker (e.g., AAPL).
B. **Company Identification:** Map ticker to CIK (for US companies) and company name.
C. **Data Acquisition:**
   - Try SEC EDGAR for US companies (10-K, 10-Q, XBRL).
   - If not available, intelligently search for the investor relations site and scrape for reports.
   - Use Yahoo Finance/Alpha Vantage as secondary sources.
D. **Data Extraction & Structuring:**
   - Parse and standardize key financial statement line items over multiple periods.
   - Handle multiple formats (HTML, PDF, XBRL).
E. **Data Validation:**
   - Cross-validate across sources.
   - Check internal consistency (e.g., balance sheet equation).
   - Score data points by confidence.
F. **Ratio Calculation:**
   - Compute a suite of ratios: liquidity, profitability, leverage, efficiency, valuation.
   - Use TTM (trailing twelve months) where appropriate.
G. **Trend/Benchmark Analysis:**
   - Calculate trends, year-over-year growth, and compare to industry/peer data.
H. **Report Generation:**
   - Generate a narrative using an LLM prompt structured with all data and calculated ratios.
   - Output PDF/HTML/Markdown with tables and charts.
I. **Logging/Audit Trail:**
   - Log data sources, timestamps, and confidence scores.
   - Handle errors gracefully, and note quality of data in the report.

**Step 6: Synthesize the Master Prompt**

- Explicitly instruct the coding AI to generate modular code (main orchestrator, data retriever, ratio calculator, report generator, etc.).
- Provide LLM prompt template for the report-writing module.
- Require robust error handling, validation, and auditability.
- Specify requirements for requirements.txt and any config files.

**Step 7: Draft the Prompt**

You will now synthesize all the above into a single, highly detailed, actionable master prompt for an AI coding tool. You will structure it so that a top-tier coding agent can autonomously produce the entire system from scratch.

---

# Master Prompt for Autonomous Financial Analysis System Generation

---

**SYSTEM PROMPT START**

You are a world-class AI Software Architect specializing in financial data engineering and modern UI/reporting. Your task is to design and generate a modular, robust, and production-ready Python application that automates financial analysis of publicly listed companies for investment decision-making.

---

## High-Level Objective

Create a Python application that takes a company stock ticker as input and, **without human intervention**, performs the following:

1. **Discovers and retrieves financial statement data** from official sources (SEC EDGAR, company investor relations, Yahoo Finance, etc.).
2. **Extracts and standardizes** key financial metrics over multiple periods.
3. **Calculates a full suite of accounting ratios** (liquidity, profitability, leverage, efficiency, valuation) with confidence scores.
4. **Benchmarks and analyzes trends and peers** to contextualize results.
5. **Generates a professional-grade investment report** (in PDF/HTML/Markdown) with narrative, tables, and charts.
6. **Implements robust error handling, validation, and audit trails** throughout.

---

## Architectural Principles

- **API-First, Scrape-Second:** Always prefer official APIs (SEC, Yahoo Finance) for data. Use web scraping only as a fallback and with respect to robots.txt and rate limits.
- **Modularity:** Organize the code into logical modules: orchestrator, data retriever, extraction/validation, ratio calculator, benchmarking, report generator, and utilities.
- **Validation:** Cross-validate data from multiple sources. Check for internal and temporal consistency. Assign a confidence score to each data point.
- **Auditability:** Log all data sources, timestamps, and errors. Include a data quality and confidence section in the report.
- **Error Handling:** All network and file operations must be robustly wrapped in try-except with graceful degradation and clear logging.
- **UI/UX:** The report output must be visually professional—charts, tables, and narrative, suitable for investment decision-making.

---

## Detailed System Specification

### 1. Main Orchestrator (`main.py`)
- Handles CLI arguments: `--ticker`, `--output [pdf/html/md]`, `--verbose`, etc.
- Orchestrates the workflow: data discovery → extraction → validation → ratio calc → analysis → report generation.
- Handles top-level error logging and user feedback.

### 2. Data Retriever Module (`data_retriever.py`)
- **Class `DataRetriever`:**
  - **`get_cik_from_ticker(ticker)`**: Queries SEC or a mapping to obtain CIK for US tickers.
  - **`get_sec_filings(cik)`**: Uses SEC EDGAR API to fetch latest 10-K/10-Q filings (with XBRL links if possible).
  - **`scrape_investor_relations(company_name)`**: If SEC fails, uses Google/Bing search to find the IR website, then scrapes for reports (PDF/HTML).
  - **`get_yahoo_finance_data(ticker)`**: Uses `yfinance` to fetch summary financials and market data as a fallback.
  - **Returns:** Structured raw data and metadata for all available sources.
  - Implements polite scraping practices (rate limiting, user-agent, robots.txt check).

### 3. Data Extraction & Structuring Module (`data_extractor.py`)
- **Class `DataExtractor`:**
  - **`parse_xbrl(file_url)`**: Extracts financial statement line items from XBRL filings.
  - **`parse_html_table(url)`**: Uses BeautifulSoup/pandas to extract tables from HTML.
  - **`parse_pdf(file_url)`**: Uses `pdfplumber` to extract tables from PDFs.
  - **Standardizes output:** Income Statement, Balance Sheet, Cash Flow Statement for 3-5 years/periods, as a dict or Pydantic model.

### 4. Data Validation Module (`data_validator.py`)
- **Class `DataValidator`:**
  - Cross-validates extracted data across sources.
  - Checks for balance sheet equation, period-over-period anomalies, and outliers.
  - Assigns confidence scores (High/Medium/Low) to each data point.
  - Logs and flags missing or inconsistent data for the report.

### 5. Ratio Calculator Module (`ratio_calculator.py`)
- **Class `RatioCalculator`:**
  - Calculates comprehensive ratios:
    - **Liquidity:** Current, Quick, Cash, OCF ratios.
    - **Profitability:** Gross, Operating, Net margins; ROE, ROA, ROIC.
    - **Leverage:** Debt-to-Equity, Debt-to-Assets, Interest Coverage.
    - **Efficiency:** Asset, Inventory, Receivables turnover, DSO.
    - **Valuation:** P/E, P/B, EV/EBITDA, P/S, PEG.
  - Handles edge cases (negative equity, missing data, zero denominators).
  - Uses TTM or multi-year averages where appropriate.
  - Annotates ratios with confidence intervals.

### 6. Benchmarking & Trend Analysis Module (`analysis.py`)
- **Class `FinancialAnalyzer`:**
  - Calculates YoY and multi-year trends for all metrics.
  - Compares ratios to industry/peer medians (use static JSON or live data if possible).
  - Flags ratios that are outliers or red flags.
  - Scores overall financial health, profitability, and risk.

### 7. Report Generator Module (`report_generator.py`)
- **Class `ReportGenerator`:**
  - Formats all validated data and ratios into a structured prompt for a generative LLM (e.g., OpenAI).
  - **LLM Prompt Template:**
    ```
    You are a Senior Financial Analyst. Given the following financial data, ratios, trends, and industry benchmarks for [Company Name], write a data-driven investment analysis report.
    **Structure:**
    1. Executive Summary
    2. Company Overview
    3. Financial Performance & Trends
    4. Ratio Analysis (with peer/industry comparison)
    5. Valuation & Recommendation
    6. Risks & Red Flags
    7. Data Quality & Confidence
    8. Data Summary Table (Markdown)
    ```
  - Calls the LLM and receives the narrative.
  - Generates a professional PDF/HTML/Markdown report using Jinja2 templates and Plotly/Matplotlib charts.
  - Includes data sources, timestamps, and data quality section.

### 8. Utilities (`utils/`)
- **Logging:** All operations log to both console and file with timestamps.
- **Config:** YAML/JSON file for API keys, settings, and mapping.
- **Exception Classes:** Custom exceptions for each module.
- **Requirements:** `requirements.txt` listing all dependencies (requests, beautifulsoup4, pandas, pdfplumber, yfinance, openai, jinja2, matplotlib, plotly, PyPDF2, etc.).

---

## Requirements for the Coding AI

- Generate clean, modular, and well-documented Python code for all the above modules.
- Use latest best practices (async where appropriate, Pydantic for models, type hints, docstrings).
- Ensure robust error handling and informative logging.
- Include sample config files and requirements.txt.
- Provide a README with usage instructions and example CLI commands.

---

**SYSTEM PROMPT END**

---
This master prompt, if given to a coding AI like Claude Code, will produce a production-quality, autonomous financial analysis system that is both robust and extensible.
