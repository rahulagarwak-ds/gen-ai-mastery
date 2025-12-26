# Workout: Infrastructure

## Drill 1: Basic Dockerfile 🟢

**Task:** Write a Dockerfile for a FastAPI app

```dockerfile
# Complete the Dockerfile

FROM python:3.12-slim

# Set working directory

# Copy requirements and install

# Copy application

# Run command
```

---

## Drill 2: Docker Compose 🟡

**Task:** Create compose file for API + PostgreSQL + Redis

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    # Build from current directory
    # Expose port 8000
    # Set environment variables

  db:
    # Use postgres:15
    # Set credentials

  redis:
    # Use redis:7-alpine
```

---

## Drill 3: Redis Cache Set/Get 🟢

**Task:** Implement basic Redis operations

```python
import redis.asyncio as redis
import json

client = redis.from_url("redis://localhost:6379")

async def cache_set(key: str, value: dict, ttl: int = 3600):
    pass

async def cache_get(key: str) -> dict | None:
    pass

# Test
await cache_set("user:1", {"name": "Alice"})
data = await cache_get("user:1")
```

---

## Drill 4: Caching Decorator 🟡

**Task:** Create a decorator that caches function results

```python
def cached(ttl: int = 600):
    def decorator(func):
        # Create cache key from function name + args
        # Return cached result if exists
        # Otherwise execute and cache
        pass
    return decorator

@cached(ttl=300)
async def expensive_operation(user_id: int) -> dict:
    await asyncio.sleep(2)  # Simulate slow operation
    return {"user_id": user_id, "data": "result"}
```

---

## Drill 5: Background Task (FastAPI) 🟢

**Task:** Use FastAPI's BackgroundTasks

```python
from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # Simulate sending
    print(f"Sending to {email}: {message}")
    time.sleep(2)

@app.post("/signup")
async def signup(email: str, background_tasks: BackgroundTasks):
    # Create user
    # Add background task to send welcome email
    pass
```

---

## Drill 6: Health Check 🟢

**Task:** Create health check endpoint

```python
@app.get("/health")
async def health():
    try:
        # Check database
        # Check redis
        # Return status
        pass
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": str(e)})
```

---

## Drill 7: Graceful Shutdown 🟡

**Task:** Implement lifespan for startup/shutdown

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect to DB, Redis
    yield
    # Shutdown: close connections
    pass

app = FastAPI(lifespan=lifespan)
```

---

## Drill 8: Multi-Stage Docker Build 🔴

**Task:** Create optimized multi-stage Dockerfile

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
# Install dependencies only

# Stage 2: Runtime
FROM python:3.12-slim
# Copy only what's needed from builder
```

---

## Self-Check

- [ ] Can write Dockerfiles for Python apps
- [ ] Can use Docker Compose for multi-service apps
- [ ] Can implement Redis caching
- [ ] Can use background tasks in FastAPI
- [ ] Can create health check endpoints
