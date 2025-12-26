# Chapter 5: Deployment — Cloud Platforms & CI/CD

> _"If it's not deployed, it's not done."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- AWS Lambda with Mangum
- Google Cloud Run
- GitHub Actions CI/CD
- Environment management
- Monitoring basics

---

## 1. AWS Lambda (Serverless)

### Setup with Mangum

```bash
uv add mangum
```

```python
# main.py
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Lambda!"}

# Lambda handler
handler = Mangum(app)
```

### Dockerfile for Lambda

```dockerfile
FROM public.ecr.aws/lambda/python:3.12

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

CMD ["app.main.handler"]
```

### Deploy with AWS SAM

```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  FastAPIFunction:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      MemorySize: 512
      Timeout: 30
      Events:
        Api:
          Type: HttpApi
    Metadata:
      Dockerfile: Dockerfile
      DockerContext: .
```

```bash
sam build
sam deploy --guided
```

---

## 2. Google Cloud Run

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Cloud Run uses PORT env variable
ENV PORT=8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]
```

### Deploy

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/my-api

# Deploy to Cloud Run
gcloud run deploy my-api \
    --image gcr.io/PROJECT_ID/my-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### With Cloud SQL

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine

# Cloud Run uses Unix socket for Cloud SQL
if os.environ.get("CLOUD_SQL_CONNECTION"):
    DATABASE_URL = f"postgresql+asyncpg://user:pass@/{db}?host=/cloudsql/{connection}"
else:
    DATABASE_URL = os.environ.get("DATABASE_URL")
```

---

## 3. GitHub Actions CI/CD

### Basic Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest

      - name: Run linter
        run: uv run ruff check .
```

### Deploy to Cloud Run

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to GCP
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2

      - name: Build and Push
        run: |
          gcloud builds submit --tag gcr.io/$PROJECT_ID/my-api

      - name: Deploy
        run: |
          gcloud run deploy my-api \
            --image gcr.io/$PROJECT_ID/my-api \
            --region us-central1
```

---

## 4. Environment Management

### Settings with Pydantic

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    openai_api_key: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment Files

```bash
# .env.development
DEBUG=true
DATABASE_URL=sqlite:///./dev.db

# .env.production (never commit!)
DEBUG=false
DATABASE_URL=postgresql://...
```

### Secrets in CI/CD

```yaml
# GitHub Actions
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## 5. Monitoring

### Logging

```python
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### Structured Logging for Cloud

```python
import json

def log_json(level: str, message: str, **extra):
    print(json.dumps({
        "severity": level,
        "message": message,
        **extra
    }))

log_json("INFO", "Request processed", path="/api", duration_ms=150)
```

---

## Quick Reference

### AWS Lambda

```python
from mangum import Mangum
handler = Mangum(app)
```

### Cloud Run

```bash
gcloud run deploy APP --image IMAGE --allow-unauthenticated
```

### GitHub Actions

```yaml
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```

---

## Summary

You've learned:

1. **AWS Lambda** — serverless FastAPI with Mangum
2. **Cloud Run** — managed containers
3. **CI/CD** — GitHub Actions workflows
4. **Environments** — Pydantic settings, secrets
5. **Monitoring** — logging for cloud

**Month 4 Complete!** You can now build and deploy production APIs.
