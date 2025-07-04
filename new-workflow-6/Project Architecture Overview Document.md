# Automated Financial Analysis System: Architecture & Technical Deep Dive

## 1. Introduction

### 1.1. Project Vision

The Automated Financial Analysis System is a sophisticated, enterprise-grade command-line tool engineered to deliver comprehensive financial intelligence on public companies. Its primary vision is to automate the laborious process of data acquisition, calculation, and interpretation, transforming raw SEC filings into polished, actionable reports. The system is designed to serve as a reliable, efficient, and extensible engine for financial research and screening, suitable for both individual analysis and integration into larger automated workflows.

### 1.2. Core Philosophy

The architecture of this system is founded on a set of robust software engineering principles designed to ensure its long-term health, maintainability, and scalability:

*   **Modularity and Separation of Concerns:** The system is decomposed into distinct, independent layers (Core, Services, Data Providers, Reporting). Each component has a single, well-defined responsibility, which simplifies development, testing, and future modifications.
*   **Data Integrity and Type Safety:** At the heart of the system lies Pydantic, which enforces strict data validation and type hinting. This ensures that data is clean, consistent, and correct as it flows through the application, drastically reducing runtime errors and making the codebase more predictable and self-documenting.
*   **Extensibility and Abstraction:** Through the use of Abstract Base Classes (e.g., `BaseDataProvider`, `BaseReporter`), the system is designed to be easily extended. New data sources or report formats can be added with minimal impact on the existing codebase, promoting a plug-and-play architecture.
*   **Dependency Injection:** The system avoids hard-coded dependencies. Instead, components are "injected" at runtime (as seen in `main.py`). This decouples the components, making them independently testable and interchangeable.
*   **Reproducibility and Portability:** The entire application stack is containerized using Docker and orchestrated with Docker Compose. This encapsulates the application, its specific Python version, all dependencies, and its services (like Redis) into a single, portable unit, guaranteeing identical behavior across any development, testing, or production environment.

### 1.3. Intended Audience

This document is intended for software developers, system architects, and DevOps engineers who will be working on, maintaining, or extending the Automated Financial Analysis System. It provides a "blueprint" of the application, detailing not just the "what" but also the "why" behind key architectural decisions.

---

## 2. System Architecture & Data Flow

### 2.1. High-Level Overview

The application operates as a linear, multi-stage pipeline orchestrated by the central `FinancialAnalysisSystem` class. When a user executes a command via the `main.py` entrypoint, a request to analyze a specific company is initiated. This request flows through a series of specialized services: data is first fetched (with caching), then numerically processed into ratios, which are then synthesized into qualitative insights. This complete, aggregated analysis is finally passed to a set of reporters that generate the user-facing output files.

### 2.2. Component Relationship Diagram

The following diagram illustrates the high-level architecture and the flow of control and data between the major components of the system.

```mermaid
graph TD
    subgraph "Host Machine Environment"
        A[User via CLI] -->|`docker compose run...`| B[main.py];
    end

    subgraph "Docker Network: financial-network"
        subgraph "Container: financial-analyzer"
            B -- 1. Instantiates & Invokes --> C{FinancialAnalysisSystem};
            
            C -- 2. `fetch_company_financials()` --> D[DataService];
            D -- 3. Tries Provider --> E[SecEdgarProvider];
            E -- 4. Checks Cache --> F[(Redis Cache)];
            F -- 5a. Cache Hit --> E;
            E -- 6a. Returns Cached Data --> D;
            
            E -- 5b. Cache Miss --> G((SEC EDGAR API));
            G -- 6b. Returns Raw JSON --> E;
            E -- 7b. Parses & Models Data --> E_Parsed[Pydantic Statement Models];
            E -- 8b. Stores in Cache --> F;
            E -- 9b. Returns Parsed Data --> D;
            
            D -- 10. Returns `CompanyInfo`, `List[FinancialStatement]` --> C;
            
            C -- 11. `calculate_ratios()` for each statement --> H[CalculationService];
            H -- 12. Returns `List[FinancialRatios]` --> C;
            
            C -- 13. `generate_qualitative_analysis()` --> I[AnalysisService];
            I -- 14. Returns `Dict` of Analysis --> C;
            
            C -- 15. Assembles Final Model --> J[CompanyAnalysis Model];
            
            C -- 16. `generate_report()` --> K[TextReporter];
            C -- 17. `generate_report()` --> L[ExcelReporter];
            
            K -- Writes to Volume --> M[<i fa fa-file-text></i> /app/reports/report.txt];
            L -- Writes to Volume --> N[<i fa fa-file-excel></i> /app/reports/report.xlsx];
        end
        
        subgraph "Container: financial-redis"
             F
        end
    end
    
    subgraph "Host Machine Filesystem"
        M -- Mapped via Volume --> O[reports/report.txt];
        N -- Mapped via Volume --> P[reports/report.xlsx];
    end

    style A fill:#d4edda,stroke:#155724
    style B fill:#fff0c1,stroke:#856404
    style G fill:#f8d7da,stroke:#721c24
    style F fill:#d1ecf1,stroke:#0c5460
    style O fill:#d4edda,stroke:#155724
    style P fill:#d4edda,stroke:#155724
```

### 2.3. Detailed Data Flow Walkthrough

Let's trace the execution of the command: `docker compose run --rm financial-analyzer python3 main.py --ticker AAPL`

1.  **Command Invocation (`main.py`):** The Docker Compose command starts a new `financial-analyzer` container and executes `main.py`. The `argparse` library parses the `--ticker AAPL` argument.

2.  **Dependency Injection (`main.py`):** The `main()` function acts as the application's composition root. It instantiates all the necessary components: `SecEdgarProvider`, `DataService`, `CalculationService`, `AnalysisService`, `TextReporter`, and `ExcelReporter`. These objects are then "injected" into the constructor of the main `FinancialAnalysisSystem`. This is a critical design pattern that decouples the orchestrator from the concrete implementations of its dependencies.

3.  **System Orchestration (`FinancialAnalysisSystem.run`):** The `run` method is called with `ticker='AAPL'`. This method defines the master sequence of operations.

4.  **Data Fetching (`DataService.fetch_company_financials`):**
    *   The system calls the `DataService`. The service iterates through its list of providers (currently just `SecEdgarProvider`).
    *   The `SecEdgarProvider` is invoked. It first needs to find the CIK for "AAPL". It checks its Redis cache for the CIK map. If not present (cache miss), it fetches `company_tickers.json` from the SEC, parses it, and stores it in Redis for future use.
    *   With the CIK, it requests the company facts data from the SEC API, again checking the Redis cache first. On a cache miss, it fetches the large JSON from `data.sec.gov`, stores it in Redis with a 24-hour expiration, and then proceeds. On a cache hit, it uses the local data instantly.
    *   The provider parses the complex JSON structure, mapping the required XBRL tags (e.g., `SalesRevenueNet`) to the clean fields in our Pydantic models (`revenue`). It instantiates and populates a `CompanyInfo` object and a list of `FinancialStatement` objects for each of the last 5 years of 10-K filings.
    *   These strongly-typed objects are returned to the `FinancialAnalysisSystem`.

5.  **Quantitative Analysis (`CalculationService.calculate_ratios`):**
    *   The system iterates through the list of `FinancialStatement` objects received from the data service.
    *   For each statement, it calls the static `calculate_ratios` method of the `CalculationService`.
    *   This service is **stateless**; its output depends only on its input. It performs arithmetic operations on the statement data (e.g., `current_assets / current_liabilities`) to compute liquidity, profitability, leverage, and efficiency ratios. The `_safe_divide` helper method ensures that division-by-zero or calculations with missing data (`None`) do not crash the program, returning `None` instead.
    *   A list of `FinancialRatios` Pydantic models is created and returned to the system.

6.  **Qualitative Synthesis (`AnalysisService.generate_qualitative_analysis`):**
    *   The system passes the list of `FinancialRatios` (sorted from most recent to oldest) to the `AnalysisService`.
    *   The service analyzes trends by comparing values from the first (latest) and last (oldest) periods.
    *   For each category (liquidity, profitability, etc.), it generates a human-readable text summary based on predefined thresholds (e.g., "A Current Ratio of `2.10` indicates a very strong ability...").
    *   The `_synthesize_findings` method creates a high-level summary, identifying key strengths and concerns by checking specific ratio values against another set of thresholds.
    *   It returns a single dictionary containing all these textual insights, including lists of strings for the strengths and concerns.

7.  **Data Aggregation (`CompanyAnalysis` Model):**
    *   Back in the `FinancialAnalysisSystem`, all the data artifacts are now assembled into the single, top-level `CompanyAnalysis` Pydantic model. This object is the canonical representation of the entire analysis run.
    *   This is where the bug I fixed was occurring. With the corrected `qualitative_analysis: Dict[str, Any]` model, Pydantic now successfully validates and creates the `final_analysis` object.

8.  **Report Generation (`BaseReporter` Interface):**
    *   The system iterates through its list of reporters (`TextReporter`, `ExcelReporter`).
    *   For each reporter, it calls the `generate_report` method, passing the complete `final_analysis` object and a generated output path.
    *   `TextReporter` builds a formatted string section by section and writes it to a `.txt` file.
    *   `ExcelReporter` uses `pandas` to create DataFrames from the model data, then uses `openpyxl` to write these to a multi-sheet `.xlsx` file, applying professional styling (colors, fonts, number formats, column widths).

9.  **Output Persistence (Docker Volumes):**
    *   The reporters write the files to the `/app/reports` directory *inside* the container.
    *   Because of the volume mapping (`./reports:/app/reports`) defined in `docker-compose.yml`, these files are instantly and simultaneously written to the `reports/` directory on the host machine, making them immediately accessible to the user. The same applies to the log files in the `logs/` directory.

---

## 3. Codebase Structure & File-by-File Analysis

A deep understanding of the codebase requires a methodical examination of its structure and the purpose of each file.

### 3.1. Directory Structure Diagram

```
automated-financial-analysis/
│
├── .env / .env.example       # Environment-specific configuration (e.g., API keys)
├── .gitignore                # Files and directories ignored by version control
├── docker-compose.yml        # Defines and orchestrates the multi-container Docker services
├── Dockerfile                # Recipe for building the main application's Docker image
├── main.py                   # CLI entry point and application composition root
├── README.md                 # High-level project documentation
├── Deployment_Guide.md       # Detailed guide for deploying the application
├── requirements.txt          # List of Python dependencies for the project
│
├── logs/                     # (Host) Directory for storing persistent log files
│   └── financial_analysis.log
│
├── reports/                  # (Host) Directory for storing generated analysis reports
│   └── (e.g., MSFT_analysis_20240520_143000.txt)
│
├── src/                      # Parent directory for all application source code
│   └── financial_analysis/   # The main Python package for the application
│       │
│       ├── __init__.py       # Makes the directory a Python package
│       ├── system.py         # Main orchestrator class (FinancialAnalysisSystem)
│       │
│       ├── core/             # --- Foundation Layer: Cross-cutting concerns ---
│       │   ├── __init__.py
│       │   ├── config.py     # Application settings management (Pydantic-Settings)
│       │   ├── logging_config.py # Centralized logging setup
│       │   └── models.py     # Canonical Pydantic data models (The "single source of truth")
│       │
│       ├── data_providers/   # --- Data Access Layer: External data fetching ---
│       │   ├── __init__.py
│       │   ├── base_provider.py      # Abstract base class for all data providers
│       │   └── sec_edgar_provider.py # Implementation for SEC EDGAR API with Redis caching
│       │
│       ├── reporting/        # --- Presentation Layer: Output generation ---
│       │   ├── __init__.py
│       │   ├── base_reporter.py      # Abstract base class for all report generators
│       │   ├── excel_reporter.py     # Implementation for .xlsx reports
│       │   └── text_reporter.py      # Implementation for .txt reports
│       │
│       └── services/         # --- Business Logic Layer: Core operations ---
│           ├── __init__.py
│           ├── analysis_service.py   # Generates qualitative insights from ratios
│           ├── calculation_service.py# Performs financial ratio calculations
│           └── data_service.py       # Orchestrates data providers, implements fallback/caching
│
└── tests/                    # --- Quality Assurance Layer: Automated tests ---
    └── services/
        └── test_calculation_service.py # Unit tests for the calculation service
```

### 3.2. File-by-File Deep Dive

#### Root Directory

*   **`Dockerfile`**: This is the blueprint for the application's runtime environment. It meticulously defines a reproducible container by starting with a specific Python version (`3.12-slim`), setting environment variables for clean imports (`PYTHONPATH`), installing necessary system libraries (`build-essential`), installing Python packages from `requirements.txt`, and finally copying the source code. The ordering of these commands is optimized to leverage Docker's layer caching, dramatically speeding up rebuilds during development.
*   **`docker-compose.yml`**: This is the orchestration manifest. It declares the two primary services: `financial-analyzer` (our Python app) and `redis` (our cache). It defines their relationship (`depends_on`), ensuring Redis starts first. Crucially, it sets up the `financial-network`, allowing the services to communicate via DNS (e.g., the Python app connects to the hostname `redis`). It also defines the critical **volume mounts** that link host directories (`./src`, `./reports`) to container directories, enabling live code reloading and persistent report storage.
*   **`main.py`**: This is the application's front door. It uses the standard `argparse` library to define and parse command-line arguments (`--ticker`, `--years`). Its most important role is as the **Composition Root**, where it performs Dependency Injection: it creates instances of all the services and reporters and passes them to the `FinancialAnalysisSystem`. This design makes the system highly decoupled and testable.
*   **`requirements.txt`**: This file lists all direct Python dependencies and their recommended versions (using `~=`). This is essential for ensuring that the Docker image is built with the exact same library versions every time, preventing "dependency hell" and ensuring reproducibility. The inclusion of `redis` is what enables the caching feature.

#### `src/financial_analysis/core/` (The Foundation Layer)

This directory contains the bedrock of the application. These components are used by all other layers.

*   **`models.py`**: This is arguably the most important file for ensuring application stability. It defines a suite of `pydantic.BaseModel` classes that serve as the "single source of truth" for the application's data structures.
    *   **Purpose & Benefit**: By defining models like `IncomeStatement`, `FinancialRatios`, and the top-level `CompanyAnalysis`, we gain runtime data validation, type enforcement, and excellent editor support (autocompletion). Any data fetched from an external API or calculated internally is immediately parsed into these models. If the data is malformed (e.g., a string where a float is expected), Pydantic raises an immediate, clear error, preventing bad data from propagating silently through the system.
    *   **Key Models**:
        *   `IncomeStatement`, `BalanceSheet`, `CashFlowStatement`: Represent the raw financial data, with every field being `Optional[float]` to gracefully handle missing data from the source.
        *   `FinancialStatement`: A composite object that groups the three statements with metadata for a single fiscal period.
        *   `FinancialRatios`: The output of the `CalculationService`, again using `Optional[float]` as not all ratios may be calculable.
        *   `CompanyAnalysis`: The final, all-encompassing data model that aggregates every piece of information for a single analysis run. It is this model that gets passed to the reporters. The fix I implemented changed `qualitative_analysis: Dict[str, str]` to `qualitative_analysis: Dict[str, Any]` to correctly model the data produced by the `AnalysisService`, which includes lists of strengths and concerns.
*   **`config.py`**: This file centralizes all application configuration. It uses the `pydantic-settings` library to create a `Settings` class that automatically loads configuration values from environment variables or, importantly, the `.env` file. This is a best practice that cleanly separates configuration from code.
*   **`logging_config.py`**: Provides a single function, `setup_logging()`, that configures logging for the entire application using a dictionary-based setup. This is more flexible than basic logging configuration. It defines two handlers: a `console` handler for `INFO`-level logs that are easily visible during interactive runs, and a rotating `file` handler for `DEBUG`-level logs that persist in the `logs/` directory for detailed post-mortem analysis. It also wisely reduces the log level for noisy HTTP libraries like `httpx` and `yfinance` to `WARNING`.

#### `src/financial_analysis/services/` (The Business Logic Layer)

This is where the core work of the application is performed.

*   **`data_service.py`**: This service acts as an abstraction layer over the various data providers. Its `fetch_company_financials` method iterates through a list of provider instances. This design is highly extensible: to add a new data source (e.g., from a different API like AlphaVantage), one would simply create a new provider class and add an instance of it to the list passed to `DataService` in `main.py`. The service implements a robust fallback mechanism: if the first provider fails, it logs a warning and automatically tries the next one in the list.
*   **`calculation_service.py`**: This service is a prime example of a **stateless utility**. It has no internal state (`__init__` does nothing) and contains only static methods. Its `calculate_ratios` method takes a `FinancialStatement` object and returns a `FinancialRatios` object. The logic is pure, predictable, and easy to unit test. The private `_safe_divide` method is a crucial piece of defensive programming, ensuring that the application never crashes due to a `ZeroDivisionError` or an operation on `None`.
*   **`analysis_service.py`**: This service contains the "intelligence" of the application, translating raw numbers into narrative insight. It takes the historical list of `FinancialRatios` and performs two key functions:
    1.  **Trend Analysis (`_get_trend`)**: A simple but effective method to determine if a metric is "improving", "declining", or "stable" by comparing the first and last data points in the series.
    2.  **Qualitative Judgment**: Methods like `_analyze_liquidity` use hard-coded thresholds to generate descriptive sentences about the company's financial state.
    3.  **Synthesis (`_synthesize_findings`)**: This method aggregates the individual analyses into a high-level executive summary, creating lists of key strengths and concerns. This is the method that produces the lists that caused the original Pydantic validation error.

#### `src/financial_analysis/data_providers/` (The Data Access Layer)

This layer is responsible for all communication with the outside world to fetch data.

*   **`base_provider.py`**: Defines the `BaseDataProvider` Abstract Base Class (ABC). This is the "contract" that all data providers must follow. By requiring `get_company_info` and `get_financial_statements` methods, it guarantees that any provider can be used interchangeably by the `DataService`. It also defines a custom `DataProviderError` for consistent error handling.
*   **`sec_edgar_provider.py`**: This is a complex and vital component.
    *   **CIK Mapping**: It first fetches a master JSON file from the SEC to map tickers (like `MSFT`) to Central Index Keys (CIK, like `0000789019`), which are the primary identifiers used by the EDGAR API.
    *   **Redis Caching (`_get_with_cache`)**: This private method is the heart of the caching implementation. Before making any network request, it first checks a Redis instance for a corresponding key. If found (a "cache hit"), the data is returned instantly. If not found (a "cache miss"), it performs the `requests.get()` call, and upon a successful response, it stores the result in Redis with a 24-hour timeout using `setex`. This logic is applied to both the CIK map and the main company facts data, making subsequent runs for the same ticker incredibly fast.
    *   **Data Parsing**: The most complex part of this provider is parsing the gigantic JSON response from the SEC's `companyfacts` endpoint. It navigates this structure to find the annual (`10-K`, `FY`) data points under `us-gaap` facts. The `XBRL_TAG_MAP` dictionary is crucial here, as it maps multiple possible XBRL tags (e.g., `Revenues`, `SalesRevenueNet`) to a single internal concept (`revenue`), handling inconsistencies in how different companies report their data. It then carefully populates the Pydantic models to be returned to the `DataService`.

#### `src/financial_analysis/reporting/` (The Presentation Layer)

This layer is responsible for creating the final, user-facing documents.

*   **`base_reporter.py`**: Similar to the provider base, this defines the `BaseReporter` ABC. It enforces a single method, `generate_report`, ensuring all reporters have a consistent interface for the `FinancialAnalysisSystem` to call.
*   **`text_reporter.py`**: This reporter builds a simple, clean, human-readable `.txt` report. It constructs the report in sections (`_format_header`, `_format_summary`, etc.) and uses the `textwrap` library to ensure the qualitative analysis paragraphs are nicely formatted and easy to read in a fixed-width view.
*   **`excel_reporter.py`**: This is a much more sophisticated reporter. It uses the powerful `pandas` library to convert the lists of Pydantic models into DataFrames, which are perfect for tabular data. It then uses `openpyxl` as its engine to write these DataFrames to a multi-sheet `.xlsx` workbook.
    *   **Advanced Features**: It goes beyond a simple data dump by applying professional formatting. The `_apply_styles` method demonstrates how to programmatically manipulate the Excel file to add header colors, bold fonts, auto-fit column widths, and apply specific number formats (e.g., currency, percentage, decimal) to different columns, resulting in a polished, presentation-ready document.

#### `tests/` (The Quality Assurance Layer)

*   **`test_calculation_service.py`**: This file demonstrates a solid approach to unit testing.
    *   **Fixtures (`@pytest.fixture`)**: It uses a fixture `sample_statement` to provide a consistent, reusable set of test data for multiple test cases.
    *   **Happy Path**: `test_calculate_ratios_happy_path` verifies that all calculations are correct when given valid, complete data.
    *   **Edge Cases**: `test_calculate_ratios_with_zero_denominator` and `test_calculate_ratios_with_none_input` are critical tests that ensure the `_safe_divide` logic works as expected and the application doesn't crash when faced with imperfect data, which is common in financial statements.

---

## 4. Deployment & Operations (Docker)

The deployment strategy using Docker and Docker Compose is a cornerstone of this project's professionalism and robustness.

*   **Dockerfile Strategy**: The `Dockerfile` is architected for both reproducibility and development speed. By pinning the Python and Debian versions in the `FROM` instruction, it guarantees a consistent environment. By structuring the commands to copy `requirements.txt` and run `pip install` *before* copying the application's source code, it masterfully leverages Docker's layer caching. This means that during active development where only `.py` files are changing, the lengthy dependency installation step is skipped, leading to near-instantaneous rebuilds.

*   **Docker Compose Orchestration**: The `docker-compose.yml` file defines the application as a holistic system, not just a single script.
    *   **Services**: It defines the `financial-analyzer` and `redis` services, giving them clear, addressable hostnames on their shared network.
    *   **Networking**: The custom `financial-network` isolates the application, which is a security best practice, and allows for simple service-to-service communication (e.g., `host=redis` in the code).
    *   **Data Persistence**: The file uses two types of volumes for two different purposes.
        1.  **Bind Mounts** (e.g., `./src:/app/src`): These are used for development convenience (live code updates) and for persisting user-facing artifacts (`reports/`, `logs/`) in a predictable location on the host.
        2.  **Named Volumes** (e.g., `redis-data`): This is used for the Redis cache. The data is managed by Docker itself, which is the recommended approach for persisting application state that the user doesn't need to directly manipulate. This ensures the cache survives `docker compose down` and `up` cycles if the volume is not explicitly removed.

*   **Execution Workflow**: The user interacts with the system through simple, declarative `docker compose` commands.
    *   `docker compose up --build`: To build and start the entire stack.
    *   `docker compose run --rm <service> ...`: The primary method for executing one-off analysis runs. The `--rm` flag is critical for preventing the accumulation of stopped containers.
    *   `docker compose down`: To cleanly shut down and remove all related resources.

---

## 5. Potential Enhancements & Future Roadmap

Based on this deep architectural review, the system is well-positioned for future growth. The following are logical next steps:

1.  **Implement a Fallback Data Provider**: The `DataService` is already designed for it. The next step is to implement a second provider (e.g., using the `yfinance` library) that can fetch data from Yahoo Finance. This would add redundancy and could also be used to fetch data (like market caps or daily prices) that the SEC API does not provide.
2.  **Asynchronous Data Fetching**: For analyses that might require fetching data from multiple sources or for multiple tickers, the I/O-bound data fetching operations could be converted to use `asyncio` and `httpx.AsyncClient` to perform network requests concurrently, significantly improving performance.
3.  **Introduce a Database**: For long-term storage and trend analysis across many different companies and time periods, the generated reports could be saved to a structured database (e.g., PostgreSQL). This would enable more powerful queries, such as "show me the average P/E ratio for all tech companies analyzed in the last quarter."
4.  **Develop a Web API**: The entire `FinancialAnalysisSystem` can be wrapped in a RESTful API using a framework like **FastAPI**. FastAPI would integrate seamlessly with the existing Pydantic models. This would transform the tool from a CLI application to a backend service that could power a web frontend or be consumed by other programs.
5.  **Enhance Test Coverage**: While the `CalculationService` has good tests, coverage should be expanded to the other services. The `DataService`'s fallback logic and the `AnalysisService`'s qualitative judgments are prime candidates for new unit tests, which would require mocking the services they depend on.

---

## 6. Conclusion

The Automated Financial Analysis System is a well-architected and robust application that demonstrates a strong adherence to modern software engineering best practices. Its modular design, reliance on data validation through Pydantic, and professional containerization strategy make it a powerful, reliable, and highly extensible platform. The codebase is clean, readable, and effectively separates concerns into logical layers. After correcting the minor data-model mismatch, the system stands as a solid foundation ready for immediate use and future expansion.

---
https://drive.google.com/file/d/15H9Ts6LBQuHE1YBy6Yt79RkYFVbwu6Sw/view?usp=sharing, https://drive.google.com/file/d/1QyJFlP4UhN5BKsrkBeLKm7Y7icieVAfb/view?usp=sharing, https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221VUSccCPl1YcCHmPUtnue6Uk-XPs5_zgO%22%5D,%22action%22:%22open%22,%22userId%22:%22108686197475781557359%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing
