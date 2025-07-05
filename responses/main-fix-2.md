```python name=src/report_generator.py
# File: src/report_generator.py
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
            # Pass 'now' to the template context as a datetime object, and flatten report_data for template context
            context = {**report_data, "company_name": company_name, "now": datetime.now()}
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(template.render(**context))
            files["html"] = str(html_file)

        logger.info(f"Report generated for {ticker}: {files}")
        return files
```
**Key points in this update:**
- Preserves your original file's structure and logging.
- Passes all of `report_data` plus `company_name` and a new `now` variable into the template context.
- Uses UTF-8 encoding for HTML.
- Ensures compatibility with the updated template that uses `{{ now.isoformat() }}`.

