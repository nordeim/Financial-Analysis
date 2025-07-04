# Why Your `financial-analyzer-2` Container Keeps Restarting

When you see  
```  
STATUS   Restarting (1) xx seconds ago  
```  
it means the container’s main process exited with code 1, and Docker’s `restart: unless-stopped` policy keeps kicking it back up.  

---

## 1. Inspect the Exit Error

1. Disable automatic restarts temporarily.  
   In your `docker-compose.yml`, under the `financial-analyzer` service, change  
   ```yaml
   restart: no
   ```  
2. Recreate the container (to pick up the `restart: no` change):  
   ```bash
   docker compose up --no-start
   docker compose start financial-analyzer
   ```  
3. Attach to its output and watch the logs live:  
   ```bash
   docker logs -f financial-analyzer-2
   ```  
   The Python traceback or error message there is your smoking gun.

---

## 2. Common Culprits

- **Missing or mis-mounted files**  
  * You bind-mounted `./main.py` over the one baked into the image. If that file is missing, empty, or has wrong permissions, `python3 main.py` will error out immediately.  
  * Ensure `./main.py` really exists in your compose folder and is readable.

- **Import/path errors**  
  * You set `ENV PYTHONPATH=/app/src`. If your `src/` folder lacks an `__init__.py` or your imports are wrong, Python raises `ModuleNotFoundError`.  

- **Unmet runtime prerequisites**  
  * If your script reads required environment variables (API keys, DB URLs) from `.env` but that file is missing or malformed, Pydantic or your own checks could abort on startup.  

- **Redis not yet ready**  
  * `depends_on` only waits for the container to start, not for Redis to accept connections. A connection refusal at launch might cause your script to crash.  

---

## 3. Debugging Workflow

1. **Run interactively**  
   ```bash
   docker compose run --service-ports --entrypoint bash financial-analyzer
   ```  
   Once inside, try:  
   ```bash
   python3 main.py --ticker MSFT
   ```  
   This surfaces errors immediately in your shell.

2. **Add a wait-for script**  
   If Redis readiness is suspect, include a small entrypoint that loops until the port’s open:  
   ```bash
   # wait-for-redis.sh
   #!/bin/sh
   until nc -z redis 6379; do
     echo "Waiting for Redis…"
     sleep 1
   done
   exec "$@"
   ```  
   Then in `docker-compose.yml`:  
   ```yaml
   entrypoint: ["./wait-for-redis.sh", "python3", "main.py", "--ticker", "MSFT"]
   ```

3. **Check file permissions**  
   Ensure `main.py` is world-readable and (if you rely on shebang) executable:  
   ```bash
   chmod 644 main.py
   ```

---

## 4. Once You’ve Found the Error

- **Fix the root cause** (typo in `main.py`, missing env var, import path)  
- Revert `restart: no` back to `unless-stopped`  
- Rebuild and relaunch:  
  ```bash
  docker compose up --build -d
  ```

---

### Extra: Building Robust Containers

- Add `HEALTHCHECK` instructions in your Dockerfile so Docker knows when your app is truly up.  
- Structure your Dockerfile with an actual entrypoint script that logs start-up steps, so you immediately know where it died.  
- Consider splitting long-running services (your analyzer) from one-off tasks (single reports) to simplify lifecycle management.

---
# Why Your Container Keeps Restarting

When your `financial-analyzer-2` service exits with code 1, Docker’s `restart: unless-stopped` policy immediately tries to bring it back up, resulting in a restart loop. Your logs reveal the root cause.

---

## 1. What the Logs Show

```text
pydantic_core._pydantic_core.ValidationError: 2 validation errors for CompanyAnalysis
qualitative_analysis.key_strengths
  Input should be a valid string … input_type=list
qualitative_analysis.key_concerns
  Input should be a valid string … input_type=list
```

Your Pydantic model `CompanyAnalysis` expects both `key_strengths` and `key_concerns` to be strings, but your analysis pipeline is passing lists. The unhandled exception bubbles up and causes Python to exit with a non-zero status.

---

## 2. Two Ways to Resolve

1. Convert lists to strings before instantiating `CompanyAnalysis`.  
2. Update your Pydantic schema to accept lists (or `str | list[str]`) and handle them downstream.

---

## 3. Converting Lists to Strings

In your `src/financial_analysis/system.py`, locate the spot where you build `CompanyAnalysis` (around line 58). Wrap any list inputs in a join:

```python
# Example snippet inside run()
raw = self._gather_qualitative(ticker)
strengths = raw.get("key_strengths", [])
concerns  = raw.get("key_concerns", [])

if isinstance(strengths, list):
    strengths = "\n".join(strengths)

if isinstance(concerns, list):
    concerns = "\n".join(concerns)

final_analysis = CompanyAnalysis(
    quantitative_analysis = ...,
    qualitative_analysis = QualitativeAnalysis(
        key_strengths = strengths,
        key_concerns  = concerns,
        overview      = raw.get("overview", "")
    )
)
```

This ensures you always pass strings.

---

## 4. Adapting the Pydantic Model

Alternatively, change your model definitions in `src/financial_analysis/models.py`:

```python
from typing import Union, List
from pydantic import BaseModel

class QualitativeAnalysis(BaseModel):
    key_strengths: Union[str, List[str]]
    key_concerns:  Union[str, List[str]]
    overview:      str
```

You can then add a custom validator to normalize the field into a single string:

```python
from pydantic import field_validator

class QualitativeAnalysis(BaseModel):
    key_strengths: Union[str, List[str]]
    key_concerns:  Union[str, List[str]]
    overview:      str

    @field_validator("key_strengths", "key_concerns", mode="before")
    def ensure_str(cls, v):
        if isinstance(v, list):
            return "\n".join(v)
        return v
```

---

## 5. Rebuild and Relaunch

1. Apply one of the fixes above.  
2. Rebuild your image and bring your stack back up:

   ```bash
   docker compose up --build -d
   ```

3. Confirm the `financial-analyzer-2` container stays `Up` instead of restarting.

---

### What Next?

Once it’s running, you might add:

- A **healthcheck** in your Dockerfile to signal readiness.  
- Logging around your entrypoint to catch early failures.  

---
# Assessing Your Proposed Fix

Your diff changes the Pydantic field from a strict `Dict[str, str]` to a more permissive `Dict[str, Any]`.  

```diff
-    qualitative_analysis: Dict[str, str]
+    qualitative_analysis: Dict[str, Any]
```

---

## 1. Immediate Effect

- Pydantic will no longer enforce that each value is a string.  
- Lists (and any other JSON-serializable type) will pass validation, so the container will stop crashing on that `ValidationError`.

---

## 2. Caveats and Downsides

- You lose type guarantees on every value under `qualitative_analysis`.  
- Downstream code that expects strings may break or need extra checks.  
- You’ll still need to handle the lists in your report generator or templates.

---

## 3. A More Targeted Alternative

Instead of `Any`, model exactly what you need:

```python
from typing import Dict, List, Union
from pydantic import BaseModel, field_validator

class CompanyAnalysis(BaseModel):
    qualitative_analysis: Dict[str, Union[str, List[str]]]
    # …

    @field_validator("qualitative_analysis", mode="before")
    def normalize_values(cls, v: Dict[str, Union[str, List[str]]]):
        normalized = {}
        for key, val in v.items():
            if isinstance(val, list):
                normalized[key] = "\n".join(val)
            else:
                normalized[key] = val
        return normalized
```

- This enforces that keys map only to strings or lists of strings.  
- You still auto-convert lists into multi-line strings, preserving downstream assumptions.

---

## 4. Recommendation

- Your `Dict[str, Any]` change will stop the startup crash immediately.  
- For long-term stability, consider one of these:  
  - Use `Union[str, List[str]]` + a validator.  
  - Split out a `QualitativeAnalysis` model with its own field validators.  

Which route feels more maintainable for your pipeline?

---
Your container now exits with code 0—success! 🎉 It ran the full pipeline, generated reports, and then cleanly shut down because your Docker default command finishes. 

---

## Keeping the Analyzer Running Continuously

If you’d prefer it stay up (for example, to serve a web API) instead of exiting:

1. Replace your `command:` with a long-lived process:
   ```yaml
   command: tail -f /dev/null
   ```
2. Or, add a web interface (Flask/FastAPI) and update both the image’s CMD and expose the port:
   ```dockerfile
   CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
3. Adjust `docker-compose.yml` accordingly:
   ```yaml
   financial-analyzer:
     ports:
       - "8000:8000"
     command: uvicorn src.api:app --host 0.0.0.0 --port 8000
   ```

Your current setup works perfectly for one-off analysis runs—just check your `/app/reports` folder on the host for results. Let me know if you want to turn this into a persistent service!

