# python src/main.py AAPL --format pdf --industry-benchmark --peer-analysis --historical-years 5

Great progress! Here’s how to **execute your workflow with Docker** after the image is built, plus answers to your likely follow-up questions:

---

## 1. **How to Run the Workflow for a Specific Ticker**

You have two main options:

### **A. Use `docker-compose` with Custom Command**

The `docker-compose.yml`’s `command:` line determines what’s run by default (currently: `AAPL --format both`).  
To run for a different ticker or options, **override the command**:

```bash
docker-compose run --rm financial-analyzer python3 src/main.py TSLA --format pdf
```

- Replace `TSLA` with any ticker and add any CLI flags your workflow supports.

**Examples:**

- Run for Microsoft, output PDF:
  ```bash
  docker-compose run --rm financial-analyzer python3 src/main.py MSFT --format pdf
  ```
- Run for multiple years with industry benchmarking:
  ```bash
  docker-compose run --rm financial-analyzer python3 src/main.py GOOGL --historical-years 7 --industry-benchmark --format both
  ```

### **B. Use `docker exec` for an Already Running Container**

If your container is running in the background (from `docker-compose up -d`), you can execute a new command inside it:

```bash
docker exec -it financial-analyzer python3 src/main.py NVDA --format html
```

---

## 2. **How to Change the Default Command**

If you want to **always analyze a different ticker or use different flags by default**:

- Edit the `command:` line in `docker-compose.yml`:

```yaml
    command: >
      python3 src/main.py TSLA --format pdf --industry-benchmark
```
Then run:
```bash
docker-compose up --build
```

---

## 3. **How to Run in Interactive Mode**

You can also open a shell in your container for debugging or running manual commands:

```bash
docker-compose run --rm financial-analyzer /bin/bash
```
Then run any Python commands you want inside the shell.

---

## 4. **What Happens with Output and Logs**

- **Reports** (PDF, HTML, etc.) are written to your repo’s `reports/` directory (mounted as a Docker volume).
- **Logs** are in `logs/` (also mounted).

---

## 5. **Handling the `'now' is undefined` Error**

Your Jinja2 report template uses `now()` but doesn’t define or pass it.
**Fix:** In your `report_generator.py`, pass the current time into the template context:

```python
from datetime import datetime

# ...inside generate()
context = dict(report_data)
context['now'] = datetime.now
with open(html_file, "w") as f:
    f.write(template.render(**context))
```
Or in your template, use Jinja’s [builtin functions](https://jinja.palletsprojects.com/en/3.0.x/templates/#date):

```html
<div class="footer">
    Generated at {{ "%Y-%m-%d %H:%M:%S"|strftime }}
</div>
```
Otherwise, always pass a `now` variable as shown.

---

## 6. **Summary Table**

| Task              | Command Example                                                                                           |
|-------------------|----------------------------------------------------------------------------------------------------------|
| Build and run     | `docker-compose up --build`                                                                              |
| Run for ticker    | `docker-compose run --rm financial-analyzer python3 src/main.py IBM --format both`                       |
| Run interactively | `docker-compose run --rm financial-analyzer /bin/bash`                                                   |
| Run inside live   | `docker exec -it financial-analyzer python3 src/main.py NFLX --format pdf`                               |
| Check reports     | `ls reports/` (on host system)                                                                           |

---

## 7. **Stopping Containers**

To stop all containers:
```bash
docker-compose down
```

---

**In summary:**  
- Use `docker-compose run --rm financial-analyzer python3 src/main.py <TICKER> [options]` for one-off runs.
- Edit `command:` in `docker-compose.yml` for default runs.
- Fix the `now` error by passing the current datetime into your template.

Let me know if you want copy-paste ready fixes for the `now` error or further workflow customization!

---
https://github.com/copilot/share/88104214-0800-80f1-9903-7c40a46149b2

