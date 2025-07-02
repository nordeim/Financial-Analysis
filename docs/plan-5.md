Below is a complete, self-contained workflow—including a reusable “master prompt” template—that you can hand to a coding-capable LLM (e.g., Claude Code, GPT-4, etc.) so it can automatically build a system that:

• Locates a public company’s latest financial statements on the web  
• Extracts the required numbers with no manual intervention  
• Calculates a full suite of accounting ratios  
• Outputs a polished, decision-ready PDF / HTML report.

Feel free to copy-and-paste the prompt, substituting your own variable values (⚙️ Parameters) whenever you run it.

---

## 1. High-Level Workflow (5 Steps)

1. Ingestion  
   a. Accept company identifiers (ticker, CIK, ISIN, or full legal name).  
   b. Resolve the official investor-relations (IR) or SEC filing URLs.

2. Retrieval  
   a. Download the latest annual (10-K) and quarterly (10-Q) filings in HTML or PDF.  
   b. Fall back to EDGAR TXT / XBRL API if IR site is missing.

3. Parsing & Normalization  
   a. Use rule-based HTML scraping for tabular data.  
   b. For PDFs, apply Tabula-like extraction or PDFPlumber.  
   c. Map diverse label variants to a canonical chart-of-accounts JSON schema (e.g., “Total revenue”, “Net sales”, “Sales, net”).

4. Ratio Computation  
   a. Store normalized line items in a pandas DataFrame.  
   b. Compute liquidity, solvency, profitability, efficiency and market-based ratios (full list below).  
   c. Flag outliers vs. sector medians (optional: load peer data from S&P Capital IQ or free APIs).

5. Report Generation  
   a. Render tables + charts via Plotly or matplotlib.  
   b. Use a Jinja2 HTML template → WeasyPrint for PDF.  
   c. Add executive summary, bullet insights, traffic-light color coding, and footnotes.

---

## 2. Accounting Ratios to Include

Liquidity  
• Current, Quick, Cash Ratios  
Solvency  
• Debt-to-Equity, Interest-Coverage, Debt-to-Assets  
Profitability  
• Gross, Operating, Net Margins  
• ROA, ROE, ROIC  
Efficiency  
• Asset Turnover, Inventory & Receivables Turnover, Days Sales Outstanding / Inventory / Payables  
Market (if price data available)  
• P/E, EV/EBITDA, P/B, Dividend Yield

---

## 3. Master Prompt Template

Replace the UPPER-CASE placeholders with actual values when you send it to the coding LLM:

```
You are a senior full-stack engineer + CPA tasked with building an automated
financial-analysis pipeline.

⚙️ PARAMETERS
  TARGET_COMPANY         = "APPLE INC"          # or ticker "AAPL"
  PERIOD_YEARS           = 3                    # how many fiscal years
  OUTPUT_FORMATS         = ["HTML", "PDF"]
  REPORT_STYLE           = "investment_memo"    # or "management_brief"
  RATIO_LIST             = "standard"           # or comma-separated overrides

DELIVERABLES
  1. Python 3.11 codebase, pip-installable.
  2. CLI entry point: `finreport <COMPANY> --years N`.
  3. Dockerfile for reproducible runs.
  4. Sample generated report for the target company.
  5. README with setup + usage docs.

SYSTEM ARCHITECTURE
  • Retrieval layer: `sec-api` for EDGAR, fallback to BeautifulSoup scraping.
  • Parsing layer: `beautifulsoup4`, `pdfplumber`, `regex`, robust against multi-column PDFs.
  • Normalization: map raw labels to canonical JSON schema (`labels_map.json`).
  • Storage: pandas DataFrames; optional SQLite cache.
  • Computation: vectorized ratio functions (`ratios.py`).
  • Reporting: Jinja2 HTML template -> WeasyPrint for PDF; Plotly for charts.
  • Error handling: if numeric field missing, log warning, continue.

CONSTRAINTS
  • Zero proprietary data. Only public filings and free market-price APIs.
  • Headless execution: no manual clicks.
  • Production-grade logging, retries & timeouts.
  • Unit tests > 80% coverage.

EXECUTION STEPS (the LLM must output code in this order)
  1. `project_layout/` scaffold using Cookiecutter-like structure.
  2. Core modules: `fetch.py`, `parse.py`, `normalize.py`, `ratios.py`, `report.py`.
  3. Unit tests using `pytest`.
  4. CLI wrapper: `cli.py`.
  5. Dockerfile + requirements.txt.

VALIDATION
  • Run integration test: `finreport {TARGET_COMPANY} --years {PERIOD_YEARS}`.
  • Confirm PDF exists and contains all chosen ratios with correct math.
  • Spot-check Net Margin calculation vs. 10-K figures.

PERFORMANCE
  • Goal: full pipeline < 90 seconds on 1-core VM, 1 GB RAM.

BEGIN NOW.
```

Copy everything between the triple back-ticks when invoking the coding LLM.

---

## 4. Tips for Best Results

1. Few-Shot Examples  
   Provide one or two miniature financial statements + expected ratio outputs to help the model learn any subtle mapping rules.

2. Incremental Execution  
   Ask the LLM to output modules one at a time so you can run quick tests before it proceeds.

3. Post-Processing Checks  
   Have the LLM print the computed ratios to stdout, then independently recompute a couple by hand (or in Excel) to verify accuracy.

4. Retrieval Edge Cases  
   • Foreign issuers may file 20-F instead of 10-K – include a conditional branch.  
   • Some PDFs are image-based – instruct the model to add Tesseract OCR fallback.

5. Rate Limits  
   SEC API has throughput ceilings. Build in exponential backoff and a local caching layer.

---

## 5. Optional Enhancements

• Peer Benchmarking: Pull peer tickers from NAICS/SIC code and compute percentile rankings.  
• Trend Forecast: Use simple ARIMA or LSTM to project next-year ratios.  
• Web Dashboard: Wrap the pipeline behind FastAPI + React for interactive viewing.  
• Cloud Function: Deploy as AWS Lambda for on-demand scaling.

---

With the above blueprint and master prompt, a capable coding-focused LLM can autonomously scaffold, code, test, and package an end-to-end financial analysis generator—delivering timely, investment-grade reports with no human data wrangling.

