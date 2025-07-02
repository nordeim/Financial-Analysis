Of course. It is an honor to be entrusted with such a significant task. Your faith is well-placed. Automating financial analysis is a complex but achievable goal that sits at the intersection of data engineering, financial acumen, and advanced AI. A simple prompt is insufficient; what is required is a **master blueprint** for an autonomous system, which a coding AI can then be prompted to build.

Here is the deep-thinking strategy, workflow, and the master prompt to guide a coding AI like "Claude Code" in creating this powerful financial analysis tool.

***

### **Part 1: The Guiding Strategy & Core Philosophy**

Before the prompt, we must establish the philosophy that ensures the system is robust, scalable, and reliable. Simply asking an AI to "scrape a website" is brittle and destined to fail. Websites change their layout, data formats vary, and network errors occur.

Our strategy is based on a **Modular, Fail-Safe, API-First Workflow**.

1.  **Modularity:** The system will not be a single, monolithic script. It will be a collection of specialized modules (Python scripts/classes) that handle distinct tasks: discovering data sources, fetching data, parsing documents, calculating ratios, and generating reports. This makes the system easier to build, debug, and upgrade.

2.  **Fail-Safe Operation:** Every step that involves external interaction (network requests, file parsing) must be wrapped in robust error handling. If one step fails, it should not crash the entire system. It should log the error and, if possible, attempt a fallback method.

3.  **API-First, Scrape-Second:** The user's request mentions "websites," which is the most challenging part. A professional-grade system should **prioritize structured data APIs** (like SEC EDGAR, or financial data providers) because they are reliable and consistent. Web scraping should be the **fallback mechanism**, not the primary one. This hybrid approach provides the best chance of success "without human intervention."

4.  **Generative AI for Both Code and Content:** We will use the coding AI in two phases:
    *   **Phase 1 (System Generation):** Use the master prompt below to generate the Python code for the entire data pipeline.
    *   **Phase 2 (Content Generation):** The generated Python system will, as its final step, call an LLM API (like GPT-4, Claude, or Gemini) with the structured financial data to write the final human-readable analysis.

### **Part 2: The Automated Workflow (System Architecture)**

This is the step-by-step process the final Python application will follow. The master prompt will instruct the AI to build code for each of these stages.

1.  **Input:** The system takes a company's stock ticker (e.g., `AAPL` for Apple Inc.) as its primary input.
2.  **Discovery Module:**
    *   **Attempt 1 (API):** Use the ticker to query the SEC EDGAR API to find links to the latest 10-K (annual) and 10-Q (quarterly) filings. This is the most reliable source for US-listed companies.
    *   **Attempt 2 (Web Scraping - Fallback):** If the API fails or for non-US companies, perform a targeted web search (e.g., "Apple Inc. investor relations" or "Siemens AG investor relations").
    *   **Scraping Logic:** The scraper will then visit the likely Investor Relations page and search for hyperlinks containing keywords like "Annual Report," "Quarterly Report," "10-K," "10-Q," "Financials." It will prioritize official filings (PDFs or XBRL/HTML filings).
3.  **Data Extraction Module:**
    *   It must handle multiple formats: HTML, PDF, and ideally XBRL/XML.
    *   For HTML/XBRL, it will parse structured tables.
    *   For PDFs, it will use an advanced parsing library to extract text and tables. This is the most error-prone step. The logic must search for financial statement keywords (e.g., "Consolidated Statements of Operations," "Consolidated Balance Sheets").
    *   **Key Challenge:** The extractor must be intelligent. It will use regular expressions and natural language understanding to find specific line items like "Total Revenue," "Net Income," "Total Assets," "Long-Term Debt," etc., and their corresponding values, accounting for variations in terminology.
4.  **Data Structuring Module:**
    *   The raw extracted data (e.g., `('Total Revenue', '$383,285 million')`) is cleaned and converted into a standardized JSON object.
    *   Example: `{ "period": "FY2023", "revenue": 383285000000, "net_income": 96995000000, ... }`
5.  **External Data Integration Module:**
    *   For market-based ratios, the system *must* fetch the current stock price and total shares outstanding using a reliable financial data library (e.g., `yfinance` in Python). This data is not in the company's report.
6.  **Ratio Calculation Module:**
    *   This pure-math module takes the structured JSON data and market data as input.
    *   It calculates a pre-defined set of key financial ratios and adds them to the JSON object.
7.  **Report Generation Module:**
    *   The system now has a complete, structured JSON object containing both raw data and calculated ratios for the last few periods.
    *   It formats this data into a clear, concise prompt.
    *   It sends this prompt to a powerful LLM API to generate the final narrative report.
8.  **Output:** The system saves a well-formatted Markdown or PDF report.

---

### **Part 3: The Master Prompt for the Coding AI**

Here is the masterful, detailed prompt. You would copy and paste this entire block into a powerful coding AI like "Claude Code" or an equivalent.

```prompt
**SYSTEM PROMPT START**

You are a world-class AI Software Architect specializing in financial technology (FinTech) and data engineering. Your task is to design and generate a complete, production-ready, and autonomous Python system for financial analysis.

**High-Level Objective:**
Create a Python application that takes a public company's stock ticker as input, automatically gathers its latest financial data, calculates key accounting and market ratios, and generates a comprehensive analysis report useful for investment decisions. The system must be designed for maximum autonomy and robustness, operating without human intervention.

**Core Architectural Principles:**
1.  **Modularity:** Structure the code into logical, separate modules (e.g., `data_retriever.py`, `ratio_calculator.py`, `report_generator.py`).
2.  **API-First, Scrape-Second:** Prioritize official APIs (like SEC EDGAR) for data retrieval. Use web scraping only as an intelligent fallback.
3.  **Robust Error Handling:** Every network request, file operation, and data parsing attempt must be enclosed in `try...except` blocks with detailed logging.
4.  **Standardized Data Structure:** Use a consistent internal data format (like a dictionary or Pydantic model) to pass data between modules.

**Detailed System Specification:**

Generate the complete Python code for the following system. Please include a `requirements.txt` file.

**1. Main Orchestrator (`main.py`)**
   - This script will be the entry point.
   - It will handle command-line arguments (e.g., `python main.py --ticker AAPL`).
   - It will orchestrate the flow by calling the different modules in sequence.
   - It will handle top-level error logging.

**2. Data Retriever Module (`data_retriever.py`)**
   - Create a class `DataRetriever`.
   - **Method 1: `get_filings_from_sec(ticker)`:**
     - Use the `requests` library to query the SEC EDGAR API (`https://data.sec.gov/submissions/CIK{cik_number}.json`). You will need a helper function to map a ticker to a CIK.
     - Parse the JSON response to find the latest 10-K and 10-Q filings. Return direct links to these documents.
   - **Method 2: `find_reports_via_scraping(company_name)`:**
     - This is the fallback. Use a library like `googlesearch-python` to search for "[Company Name] Investor Relations".
     - Use `requests` and `BeautifulSoup4` to parse the top search result.
     - On the Investor Relations page, intelligently search for hyperlinks containing keywords: "10-K", "10-Q", "Annual Report", "Quarterly Report", "Financial Statements". Prioritize filings with the most recent year. Return the URLs.
   - **Method 3: `extract_financial_data(document_url)`:**
     - This is the core extraction logic. It must detect the file type (HTML or PDF).
     - **For HTML:** Use `BeautifulSoup4` and `pandas.read_html` to parse tables. Search for tables preceded by headers like "Consolidated Statements of Operations", "Consolidated Balance Sheets".
     - **For PDF:** Use the `pdfplumber` library, which is excellent for extracting text and tables from PDFs.
     - **Intelligent Data Point Extraction:** For each financial statement (Income, Balance Sheet, Cash Flow), extract the following key line items for the last two fiscal periods available in the report. Use `regex` to find the line item text (e.g., `re.search(r'(?i)total revenue|net sales', text)`) and then extract the corresponding numerical value. Account for negative values in parentheses and units (e.g., "in millions").
     - **Required Data Points:**
       - **Income Statement:** Total Revenue, Gross Profit, Operating Income, Net Income.
       - **Balance Sheet:** Cash and Cash Equivalents, Total Current Assets, Total Assets, Total Current Liabilities, Total Liabilities, Total Stockholders' Equity.
       - **Cash Flow Statement:** Net Cash from Operating Activities, Capital Expenditures, Free Cash Flow (Operating Cash Flow - Capex).
   - **Return Value:** The extractor should return a list of dictionaries, one for each period found, in a standardized format: `{'period': 'Q4 2023', 'revenue': 12345, ...}`.

**3. Market Data Module (`market_data.py`)**
   - Create a function `get_market_data(ticker)`.
   - Use the `yfinance` library to get the current stock price, market capitalization, and total shares outstanding for the given ticker.
   - Return this data in a dictionary.

**4. Ratio Calculator Module (`ratio_calculator.py`)**
   - Create a class `RatioCalculator`.
   - It will take the structured financial data from the retriever and the market data as input.
   - It must calculate the following ratios. Provide the formula in the comments for each calculation.
     - **Profitability Ratios:**
       - Gross Profit Margin
       - Operating Profit Margin
       - Net Profit Margin
     - **Liquidity Ratios:**
       - Current Ratio
     - **Solvency Ratios:**
       - Debt-to-Equity Ratio
     - **Market Valuation Ratios:**
       - Price-to-Earnings (P/E) Ratio
       - Price-to-Sales (P/S) Ratio
   - It should append these calculated ratios to the main data dictionary.

**5. Report Generator Module (`report_generator.py`)**
   - Create a class `ReportGenerator`.
   - It will take the final, enriched data dictionary (raw financials + ratios) as input.
   - It will have one method: `generate_text_report(data)`.
   - **This method will make an API call to a generative LLM (e.g., using the `openai` library).**
   - Construct a detailed prompt for the LLM. The prompt should include all the extracted data and ratios, clearly formatted.
   - **The prompt to the LLM should be:**
     ```
     "You are a Senior Financial Analyst. Based on the following financial data for [Company Name] for periods [Period 1] and [Period 2], write a concise investment analysis report.
     
     **Data:**
     [Insert the clean JSON data here]
     
     **Report Structure:**
     1.  **Executive Summary:** A 3-sentence summary of the company's financial health and performance.
     2.  **Profitability Analysis:** Comment on the margins (Gross, Operating, Net) and their trends.
     3.  **Liquidity & Solvency:** Briefly assess the company's short-term health (Current Ratio) and long-term leverage (Debt-to-Equity).
     4.  **Market Valuation:** Interpret the P/E and P/S ratios. Is the stock potentially overvalued or undervalued based on these metrics?
     5.  **Data Summary Table:** Present the key data points and ratios in a clean Markdown table.
     
     Be objective and data-driven in your analysis."
     ```
   - The function will return the LLM's generated text response.

**6. `requirements.txt`**
   - Create this file listing all necessary libraries:
     ```
     requests
     beautifulsoup4
     lxml
     pandas
     pdfplumber
     yfinance
     openai
     # Add googlesearch-python or equivalent if you use one
     ```

Please now generate the complete, multi-file Python application based on this architecture. Ensure the code is clean, well-commented, and follows best practices.

**SYSTEM PROMPT END**
```

---
https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221Okb21IASfB9dVk-vsqEERTpL_h6vG3nL%22%5D,%22action%22:%22open%22,%22userId%22:%22103961307342447084491%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing
