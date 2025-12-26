# Workout: Deployment

## Drill 1: Mangum Handler 🟢

**Task:** Add Lambda handler to FastAPI app

```python
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello"}

# Add Lambda handler

```

---

## Drill 2: Pydantic Settings 🟢

**Task:** Create settings class for environment variables

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Add fields for:
    # - debug (bool, default False)
    # - database_url (str, required)
    # - openai_api_key (str, required)

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Drill 3: GitHub Actions CI 🟡

**Task:** Write a CI workflow

```yaml
# .github/workflows/ci.yml
# Create workflow that:
# - Runs on push to main
# - Sets up Python 3.12
# - Installs dependencies with uv
# - Runs pytest
# - Runs ruff linter
```

---

## Drill 4: Cloud Run Dockerfile 🟡

**Task:** Create Dockerfile for Cloud Run

```dockerfile
# Create Dockerfile that:
# - Uses python:3.12-slim
# - Installs dependencies
# - Uses PORT environment variable
# - Runs uvicorn
```

---

## Drill 5: Structured Logging 🟢

**Task:** Implement JSON logging for cloud

```python
import json
from datetime import datetime

def log(level: str, message: str, **extra):
    """Log in cloud-friendly JSON format."""
    pass

# Usage
log("INFO", "Request processed", path="/api", duration_ms=150)
# Should print: {"severity": "INFO", "message": "...", "path": "/api", ...}
```

---

## Drill 6: Request Logging Middleware 🟡

**Task:** Log all requests

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log incoming request
    # Track duration
    # Log response status
    pass
```

---

## Self-Check

- [ ] Can add Mangum handler for Lambda
- [ ] Can configure settings from environment
- [ ] Can write GitHub Actions workflow
- [ ] Can create Cloud Run compatible Dockerfile
- [ ] Can implement structured logging
