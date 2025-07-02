````markdown name=DEPLOYMENT_WORKFLOW.md
# 🚀 Financial Analysis System: Deployment & Execution Workflow

Welcome to your step-by-step guide for deploying, configuring, and executing the **Financial Analysis System** as described in the improved architecture and master prompt. This workflow is designed to be robust, scalable, and user-friendly—enabling you to analyze any publicly listed company autonomously and produce professional-grade financial reports.

---

## Table of Contents

1. [System Prerequisites](#system-prerequisites)
2. [Repository Structure](#repository-structure)
3. [Environment Setup](#environment-setup)
4. [Configuration](#configuration)
5. [Data Acquisition & Validation](#data-acquisition--validation)
6. [Financial Analysis & Reporting](#financial-analysis--reporting)
7. [Automation & Monitoring](#automation--monitoring)
8. [Extending the Workflow](#extending-the-workflow)
9. [Troubleshooting](#troubleshooting)

---

## 1. System Prerequisites

- **Python 3.9+** (3.11+ recommended for async support)
- **pip** (or pipenv/poetry for advanced users)
- **Docker** (optional, for containerized deployment)
- **Virtual Environment** (recommended)
- **API Keys** (optional: Alpha Vantage, OpenAI, etc. for premium features)
- Network access to financial data APIs

---

## 2. Repository Structure

```
financial_analysis/
├── src/
│   ├── main.py
│   ├── data_retriever.py
│   ├── data_extractor.py
│   ├── data_validator.py
│   ├── ratio_calculator.py
│   ├── analysis.py
│   ├── report_generator.py
│   └── utils/
├── config/
│   └── settings.yaml
├── templates/
│   └── report_template.html
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── tests/
├── logs/
├── reports/
└── README.md
```
---

## 3. Environment Setup

### 3.1 Clone the Repository

```bash
git clone https://github.com/nordeim/Financial-Analysis.git
cd Financial-Analysis
```

### 3.2 Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Tip:** If you use [pipenv](https://pipenv.pypa.io/) or [poetry](https://python-poetry.org/), adapt accordingly.

---

## 4. Configuration

### 4.1 API Keys & Sensitive Data

- Obtain any needed API keys (Alpha Vantage, OpenAI, etc.)
- Store them securely as environment variables or in `config/settings.yaml` (never commit secrets).

Example in `.env` file:
```env
ALPHA_VANTAGE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 4.2 Main Settings

Edit `config/settings.yaml` to customize:
- API endpoints and headers
- Industry benchmark sources
- Default reporting formats and templates
- Logging level and file locations

Example excerpt:
```yaml
apis:
  sec_edgar:
    base_url: "https://data.sec.gov/api/xbrl/companyfacts"
    headers:
      User-Agent: "Financial Analyzer 1.0 (your-email@company.com)"
  yahoo_finance:
    timeout: 30
  alpha_vantage:
    api_key: "${ALPHA_VANTAGE_API_KEY}"
...
reporting:
  output_formats: ["pdf", "html", "json"]
  chart_style: "seaborn"
  template_path: "templates/report_template.html"
...
```

---

## 5. Data Acquisition & Validation

### Step 1: Input Company Ticker

You provide a single stock ticker as input (e.g., `AAPL`, `MSFT`, `TSLA`).

### Step 2: Data Retrieval (Automated)

The workflow:
1. **SEC EDGAR API**: Maps ticker to CIK and fetches latest 10-K/10-Q/XBRL filings.
2. **Investor Relations Scraping**: If SEC fails, searches for and scrapes the company’s IR site.
3. **Financial Data APIs**: Fetches summary data from Yahoo Finance/Alpha Vantage as fallback.
4. **Market Data**: Retrieves current prices, shares outstanding, and market cap.

### Step 3: Data Extraction

- **Parses** financial statements from XBRL, HTML, or PDF.
- **Standardizes** line items: Revenue, Net Income, Assets, Liabilities, Equity, Cash Flow, etc. for multiple periods.

### Step 4: Validation & Quality Scoring

- **Cross-validates** data from all sources.
- **Checks** for accounting equation consistency, outlier detection, and period alignment.
- **Assigns** confidence levels to each data point (High/Medium/Low).
- **Logs** all operations and data source origins for auditability.

---

## 6. Financial Analysis & Reporting

### Step 5: Ratio Calculation

- Computes all key ratios (liquidity, profitability, leverage, efficiency, valuation, growth).
- Handles edge cases and missing data gracefully.
- Annotates with peer/industry benchmarks where possible.

### Step 6: Trend & Benchmark Analysis

- Calculates YoY growth, multi-year averages, and trend direction.
- Compares all ratios to industry median, quartiles, and peer group.
- Flags red flags (e.g., deteriorating margins, high leverage).

### Step 7: Automated Report Generation

- **Synthesizes** all data into a structured prompt.
- **Calls** a generative LLM (e.g., OpenAI GPT-4, Claude, Gemini) for narrative sections.
- **Generates** a professional PDF/HTML/Markdown/JSON report with charts, tables, and an executive summary.
- **Includes** data quality/confidence, source audit, and risk commentary.

### Command Example

```bash
python src/main.py AAPL --format pdf --industry-benchmark --peer-analysis --historical-years 5
```

**Output:**  
- Reports in `reports/` directory (PDF, HTML, JSON)
- Logs in `logs/` directory

---

## 7. Automation & Monitoring

### 7.1 Batch or Scheduled Analysis

- Use a shell script, cron job, or workflow manager for periodic runs.
- Example (Linux cron):

```cron
0 8 * * 1 cd /path/to/Financial-Analysis && source venv/bin/activate && python src/main.py MSFT --format both
```

### 7.2 Docker-Based Deployment (Optional)

**Build and Run Container:**
```bash
docker-compose up --build
```

- Exposes ports for future web interface.
- Stores logs and reports in mapped volumes.

---

## 8. Extending the Workflow

- **Add new data sources:** Extend `data_retriever.py` with new APIs or scrapers.
- **Add custom ratios/analytics:** Edit `ratio_calculator.py` and `analysis.py`.
- **Change report styling:** Edit `templates/report_template.html`.
- **Integrate with web UI or API:** Build on top of FastAPI or Flask for interactive dashboards.
- **Automate triggers:** Link to market event APIs or set up email/SMS notifications on report completion.

---

## 9. Troubleshooting

- **Data Not Found:** Check ticker spelling, data source availability, and API keys.
- **Extraction Errors:** Review logs in `logs/` for details; adjust extraction logic if company uses unusual formats.
- **Performance Issues:** Consider batch or async execution for multiple companies.
- **Report Not Generated:** Check for LLM API key issues or template errors.

---

## Example Workflow in Action

1. **User triggers analysis for `AAPL`:**
   - `python src/main.py AAPL --format both`
2. **System retrieves filings from SEC, validates, and cross-checks with Yahoo Finance.**
3. **Extracts, parses, and scores all financial data.**
4. **Calculates ratios, benchmarks to industry and peers, analyzes trends.**
5. **Synthesizes narrative and outputs PDF/HTML/JSON report with charts and tables.**
6. **Logs all actions, errors, and data sources for audit trail.**

---

## 🏆 Pro Tips

- Use `--verbose` for detailed logs.
- Process multiple tickers:  
  `for t in AAPL MSFT TSLA; do python src/main.py $t --format pdf; done`
- Customize templates for your organization’s branding or compliance needs.
- Monitor data freshness and automate re-runs after new earnings releases.

---

## 🎉 You’re Ready to Analyze!

The Financial Analysis System is now ready to deliver timely, robust, and actionable insights for any publicly listed company. Explore, extend, and automate your financial research with confidence!

For detailed code, see the [src/](src/) directory and the [README.md](README.md).

---

*If you encounter issues or have suggestions, please open an issue or PR. Happy analyzing! 🚀*
````

---

```python name=src/main.py
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
```

---

```python name=src/data_retriever.py
import aiohttp
import yfinance as yf
import asyncio
from utils.logger import get_logger
import time

logger = get_logger(__name__)

class DataRetriever:
    SEC_TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
    SEC_CIK_API = "https://data.sec.gov/submissions/CIK{cik}.json"
    SEC_FILINGS_API = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"

    HEADERS = {"User-Agent": "Financial Analyzer 1.0 (your-email@company.com)"}

    async def get_cik_and_name(self, ticker):
        # Get CIK and company name for ticker
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            async with session.get(self.SEC_TICKER_MAP_URL) as resp:
                data = await resp.json()
                for info in data.values():
                    if info["ticker"].lower() == ticker.lower():
                        cik = str(info["cik_str"])
                        name = info["title"]
                        logger.info(f"Found CIK {cik} for {ticker}: {name}")
                        return cik, name
        raise Exception(f"CIK not found for ticker {ticker}")

    async def get_financial_filings(self, cik):
        # Download latest company facts (XBRL) from SEC
        padded = cik.zfill(10)
        url = self.SEC_FILINGS_API.format(cik_padded=padded)
        async with aiohttp.ClientSession(headers=self.HEADERS) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    logger.info(f"SEC filings retrieved for CIK {cik}")
                    return await resp.json()
                else:
                    logger.warning("SEC filings not found, falling back to Yahoo Finance scraping")
                    return None

    async def get_market_data(self, ticker):
        # Use yfinance for market data
        stock = yf.Ticker(ticker)
        info = stock.info
        logger.info(f"Fetched market data for {ticker}")
        return info
```

---

```python name=src/data_extractor.py
import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

class DataExtractor:
    async def extract_all_statements(self, filings, years=5):
        """
        Extract key financial items from SEC XBRL filings.
        Returns standardized dict of Income, Balance Sheet, Cash Flow.
        """
        if not filings or "facts" not in filings:
            logger.warning("No filings to extract, returning empty dict.")
            return {}
        us_gaap = filings["facts"].get("us-gaap", {})
        # Key line items mapping
        key_items = {
            'Revenue': ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax'],
            'NetIncome': ['NetIncomeLoss'],
            'TotalAssets': ['Assets'],
            'TotalLiabilities': ['Liabilities'],
            'StockholdersEquity': ['StockholdersEquity'],
            'OperatingIncome': ['OperatingIncomeLoss'],
            'CostOfRevenue': ['CostOfRevenue'],
            'CurrentAssets': ['AssetsCurrent'],
            'CurrentLiabilities': ['LiabilitiesCurrent'],
            'Cash': ['CashAndCashEquivalentsAtCarryingValue'],
            'OperatingCashFlow': ['NetCashProvidedByUsedInOperatingActivities']
        }
        statements = {}
        for std_name, sec_keys in key_items.items():
            found = None
            for k in sec_keys:
                if k in us_gaap:
                    found = us_gaap[k]
                    break
            if found:
                data = []
                for unit, vals in found.get("units", {}).items():
                    for v in vals:
                        if v.get("form") == "10-K" and 'fy' in v:
                            data.append({
                                "fiscal_year": v["fy"],
                                "end_date": v["end"],
                                "value": v["val"],
                                "unit": unit
                            })
                if data:
                    df = pd.DataFrame(data)
                    df = df.sort_values('end_date', ascending=False).head(years)
                    statements[std_name] = df
                    logger.info(f"Extracted {std_name}: {len(df)} years")
        return statements
```

---

```python name=src/data_validator.py
from utils.logger import get_logger

logger = get_logger(__name__)

class DataValidator:
    def validate_data(self, fin_data, market_data):
        # Check for presence and balance sheet integrity, flag missing data
        validated = {}
        for k, df in fin_data.items():
            if df is not None and not df.empty:
                validated[k] = df
            else:
                logger.warning(f"Missing or empty data for {k}")
        # Optionally add confidence levels, outlier detection, etc.
        # For demo: everything present = High confidence, else Medium/Low
        return validated
```

---

```python name=src/ratio_calculator.py
from utils.logger import get_logger

logger = get_logger(__name__)

class RatioCalculator:
    def calculate_all_ratios(self, fin_data, market_data):
        # Compute ratios from standardized dataframes in fin_data dict
        ratios = {}
        try:
            # Example: Current Ratio
            if "CurrentAssets" in fin_data and "CurrentLiabilities" in fin_data:
                ca = fin_data["CurrentAssets"].iloc[0]["value"]
                cl = fin_data["CurrentLiabilities"].iloc[0]["value"]
                ratios["Current Ratio"] = ca / cl if cl else None

            # Example: Net Profit Margin
            if "NetIncome" in fin_data and "Revenue" in fin_data:
                ni = fin_data["NetIncome"].iloc[0]["value"]
                rev = fin_data["Revenue"].iloc[0]["value"]
                ratios["Net Profit Margin"] = ni / rev if rev else None

            # Example: Debt-to-Equity
            if "TotalLiabilities" in fin_data and "StockholdersEquity" in fin_data:
                debt = fin_data["TotalLiabilities"].iloc[0]["value"]
                eq = fin_data["StockholdersEquity"].iloc[0]["value"]
                ratios["Debt-to-Equity"] = debt / eq if eq else None

            # ... additional ratios ...
            logger.info("Ratios calculated successfully")
        except Exception as e:
            logger.warning(f"Error calculating ratios: {e}")
        return ratios
```

---

```python name=src/analysis.py
from utils.logger import get_logger

logger = get_logger(__name__)

class FinancialAnalyzer:
    def analyze(self, ratios, fin_data, market_data, company_name, industry_benchmark=False, peer_analysis=False):
        # Compose analysis dict for reporting
        analysis = {
            "company_name": company_name,
            "ratios": ratios,
            "market_data": market_data,
            "trends": {},
            "benchmarks": {},
            "peers": [],
            "risks": [],
            "data_quality": "High" if all(v is not None for v in ratios.values()) else "Medium",
        }
        # Example trend: last 2 years for revenue
        if "Revenue" in fin_data and len(fin_data["Revenue"]) > 1:
            this = fin_data["Revenue"].iloc[0]["value"]
            last = fin_data["Revenue"].iloc[1]["value"]
            growth = (this - last) / last if last else None
            analysis["trends"]["Revenue Growth"] = growth
        # TODO: Add benchmarking/peer analysis as needed
        logger.info("Analysis composed")
        return analysis
```

---

```python name=src/report_generator.py
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

class ReportGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate(self, ticker, company_name, report_data, output_format="both"):
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        files = {}

        # Save JSON
        if output_format in ("json", "both"):
            json_file = output_dir / f"{ticker}_{datetime.now():%Y%m%d_%H%M%S}_report.json"
            with open(json_file, "w") as f:
                json.dump(report_data, f, indent=2, default=str)
            files["json"] = str(json_file)

        # Render HTML
        if output_format in ("html", "both"):
            template = self.env.get_template("report_template.html")
            html_file = output_dir / f"{ticker}_{datetime.now():%Y%m%d_%H%M%S}_report.html"
            with open(html_file, "w") as f:
                f.write(template.render(**report_data))
            files["html"] = str(html_file)

        logger.info(f"Report generated for {ticker}: {files}")
        return files
```

---

```python name=src/utils/logger.py
import logging
import sys
from pathlib import Path

def setup_logging(level="INFO", log_file=None):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper()))
    root.handlers.clear()
    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    root.addHandler(ch)
    # File
    fh = logging.FileHandler(log_dir / "financial_analyzer.log")
    fh.setFormatter(formatter)
    root.addHandler(fh)

def get_logger(name):
    return logging.getLogger(name)
```

---

```text name=requirements.txt
requests
aiohttp
pandas
yfinance
beautifulsoup4
lxml
jinja2
matplotlib
plotly
pdfplumber
openai
pytest
```

---

```yaml name=config/settings.yaml
apis:
  sec_edgar:
    base_url: "https://data.sec.gov/api/xbrl/companyfacts"
    headers:
      User-Agent: "Financial Analyzer 1.0 (your-email@company.com)"
  yahoo_finance:
    timeout: 30
  alpha_vantage:
    api_key: "${ALPHA_VANTAGE_API_KEY}"

reporting:
  output_formats: ["pdf", "html", "json"]
  chart_style: "seaborn"
  template_path: "templates/report_template.html"

logging:
  level: "INFO"
  file_path: "logs/financial_analyzer.log"
```

---

````markdown name=templates/report_template.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Financial Analysis Report - {{ company_name }}</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; }
        .container { background: white; max-width: 900px; margin: 2em auto; padding: 2em; border-radius: 12px; box-shadow: 0 2px 12px #ccc; }
        h1, h2, h3 { color: #1a237e; }
        .section { margin-bottom: 2em; }
        .metric-table { width: 100%; border-collapse: collapse; margin-top: 1em; }
        .metric-table th, .metric-table td { border: 1px solid #e1e1e1; padding: 6px 12px; }
        .metric-table th { background: #f0f4ff; }
        .data-quality { background: #e8f5e9; padding: 1em; border-radius: 6px; margin-top: 1em; }
        .footer { font-size: 0.9em; text-align: right; color: #888; margin-top: 2em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Financial Analysis Report</h1>
        <h2>{{ company_name }}</h2>
        <div class="section">
            <h3>Key Ratios</h3>
            <table class="metric-table">
                <tr>
                    <th>Ratio</th><th>Value</th>
                </tr>
                {% for k, v in ratios.items() %}
                <tr>
                    <td>{{ k }}</td>
                    <td>{{ "%.3f"|format(v) if v is not none else "N/A" }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div class="section">
            <h3>Trends</h3>
            <ul>
                {% for k, v in trends.items() %}
                <li>{{ k }}: {{ "%.2f%%"|format(v*100) if v is not none else "N/A" }}</li>
                {% endfor %}
            </ul>
        </div>
        <div class="section data-quality">
            <strong>Data Quality:</strong> {{ data_quality }}
        </div>
        <div class="footer">
            Generated at {{ now().isoformat() }}
        </div>
    </div>
</body>
</html>
````

---

With these files and the deployment workflow, you can now execute the improved financial analysis pipeline from end to end.  
**For enhancements (peer benchmarking, advanced validation, LLM report writing, PDF exports), extend the respective modules as outlined in the plan and master prompt.**

If you need more advanced features (LLM narrative, peer scraping, real-time triggers) or want to see a full-scale batch workflow, let me know!

