# Chapter 4: Infrastructure — Docker, Redis, Workers

> _"Production means reproducibility. Docker is your foundation."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Docker containerization basics
- Docker Compose for multi-service apps
- Redis for caching and queues
- Background workers with ARQ/Celery
- Production patterns

---

## 1. Docker Basics

### Dockerfile for FastAPI

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Run
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t my-api .

# Run container
docker run -p 8000:8000 my-api

# Run with environment variables
docker run -p 8000:8000 -e DATABASE_URL=... my-api
```

### Multi-Stage Build (Smaller Image)

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## 2. Docker Compose

### Basic Compose File

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - '8000:8000'
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/app
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=app
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  postgres_data:
```

### Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Stop all
docker compose down

# Rebuild and start
docker compose up -d --build
```

---

## 3. Redis Caching

### Setup

```bash
uv add redis
```

### Basic Usage

```python
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost:6379")

# Set/Get
await redis_client.set("key", "value", ex=3600)  # expires in 1 hour
value = await redis_client.get("key")

# JSON caching
import json

async def cache_set(key: str, data: dict, ttl: int = 3600):
    await redis_client.set(key, json.dumps(data), ex=ttl)

async def cache_get(key: str) -> dict | None:
    data = await redis_client.get(key)
    return json.loads(data) if data else None
```

### Caching Decorator

```python
import functools
import hashlib
import json

def cached(ttl: int = 3600):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function and args
            key = f"{func.__name__}:{hashlib.md5(json.dumps([args, kwargs]).encode()).hexdigest()}"

            # Check cache
            cached_result = await cache_get(key)
            if cached_result:
                return cached_result

            # Execute and cache
            result = await func(*args, **kwargs)
            await cache_set(key, result, ttl)
            return result
        return wrapper
    return decorator

@cached(ttl=600)
async def get_expensive_data(user_id: int) -> dict:
    # This will be cached for 10 minutes
    ...
```

### LLM Response Caching

```python
async def get_cached_llm_response(prompt: str, model: str) -> str | None:
    key = f"llm:{model}:{hashlib.md5(prompt.encode()).hexdigest()}"
    return await redis_client.get(key)

async def cache_llm_response(prompt: str, model: str, response: str, ttl: int = 3600):
    key = f"llm:{model}:{hashlib.md5(prompt.encode()).hexdigest()}"
    await redis_client.set(key, response, ex=ttl)
```

---

## 4. Background Workers

### Option A: ARQ (Async-native)

```bash
uv add arq
```

```python
# tasks.py
from arq import create_pool
from arq.connections import RedisSettings

async def send_email(ctx, to: str, subject: str, body: str):
    # Simulate email sending
    print(f"Sending email to {to}")
    await asyncio.sleep(2)
    return "sent"

class WorkerSettings:
    functions = [send_email]
    redis_settings = RedisSettings(host='redis')

# Enqueue task
async def queue_email(to: str, subject: str, body: str):
    pool = await create_pool(RedisSettings())
    await pool.enqueue_job('send_email', to, subject, body)
```

```bash
# Run worker
arq tasks.WorkerSettings
```

### Option B: Celery (Traditional)

```bash
uv add celery[redis]
```

```python
# celery_app.py
from celery import Celery

app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@app.task
def process_document(doc_id: int):
    # Long-running task
    ...
    return {"status": "done"}

# Enqueue
process_document.delay(123)
```

### FastAPI Integration

```python
from fastapi import BackgroundTasks

@app.post("/upload")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    doc_id = await save_document(file)

    # Quick background task (FastAPI built-in)
    background_tasks.add_task(process_document, doc_id)

    # Or use ARQ/Celery for heavy tasks
    await queue_processing_job(doc_id)

    return {"doc_id": doc_id, "status": "processing"}
```

---

## 5. Production Patterns

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    try:
        # Check database
        await session.execute(text("SELECT 1"))

        # Check redis
        await redis_client.ping()

        return {"status": "healthy"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )
```

### Graceful Shutdown

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await redis_client.close()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
```

### Docker Compose with Workers

```yaml
services:
  api:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0

  worker:
    build: .
    command: arq app.tasks.WorkerSettings
    depends_on:
      - redis

  scheduler:
    build: .
    command: arq app.tasks.SchedulerSettings
```

---

## Quick Reference

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
```

### Docker Compose

```bash
docker compose up -d
docker compose logs -f
docker compose down
```

### Redis

```python
await redis_client.set("key", "value", ex=3600)
value = await redis_client.get("key")
```

### ARQ

```python
await pool.enqueue_job('task_name', arg1, arg2)
```

---

## Summary

You've learned:

1. **Docker** — containerization, multi-stage builds
2. **Compose** — multi-service orchestration
3. **Redis** — caching, session storage
4. **Workers** — ARQ/Celery for background tasks
5. **Production** — health checks, graceful shutdown

Next chapter: Deployment — AWS Lambda, Cloud Run, CI/CD.
