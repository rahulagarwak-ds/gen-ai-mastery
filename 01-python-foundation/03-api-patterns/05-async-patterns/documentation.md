# Chapter 5: Async Patterns

> _"Async makes your API fly — when used correctly."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- async/await fundamentals
- Async vs sync endpoints
- Concurrent HTTP requests
- Async database access
- Common async pitfalls
- When to use async

---

## 1. Async Basics

### Sync vs Async

```python
# Sync - blocks while waiting
def fetch_data():
    response = requests.get(url)  # Waits here
    return response.json()

# Async - releases control while waiting
async def fetch_data():
    response = await httpx.get(url)  # Other code can run
    return response.json()
```

### FastAPI Endpoints

```python
# Both work in FastAPI

# Sync endpoint (for CPU-bound work)
@app.get("/sync")
def sync_endpoint():
    return compute_something()

# Async endpoint (for I/O-bound work)
@app.get("/async")
async def async_endpoint():
    return await fetch_from_api()
```

---

## 2. httpx — Async HTTP Client

### Installation

```bash
uv add httpx
```

### Basic Usage

```python
import httpx

# Async context manager (recommended)
async def fetch_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        response.raise_for_status()
        return response.json()

# In FastAPI endpoint
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return await fetch_user(user_id)
```

### POST with JSON

```python
async def create_user(data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/users",
            json=data,
            headers={"Authorization": "Bearer token"}
        )
        return response.json()
```

---

## 3. Concurrent Requests

### Sequential (Slow)

```python
async def fetch_all_sequential(urls: list[str]):
    results = []
    for url in urls:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            results.append(response.json())
    return results
# 5 URLs × 100ms = 500ms total
```

### Concurrent (Fast)

```python
import asyncio

async def fetch_all_concurrent(urls: list[str]):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]
# 5 URLs = ~100ms total (parallel)
```

### With Error Handling

```python
async def fetch_all_safe(urls: list[str]):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for url, response in zip(urls, responses):
            if isinstance(response, Exception):
                results.append({"url": url, "error": str(response)})
            else:
                results.append(response.json())
        return results
```

---

## 4. Semaphores — Limiting Concurrency

```python
import asyncio
import httpx

semaphore = asyncio.Semaphore(10)  # Max 10 concurrent requests

async def fetch_with_limit(client: httpx.AsyncClient, url: str):
    async with semaphore:
        response = await client.get(url)
        return response.json()

async def fetch_many(urls: list[str]):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_with_limit(client, url) for url in urls]
        return await asyncio.gather(*tasks)
```

---

## 5. Reusable HTTP Client

### Application Lifecycle

```python
from contextlib import asynccontextmanager
import httpx

class AppState:
    http_client: httpx.AsyncClient | None = None

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    state.http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_connections=100)
    )
    yield
    # Shutdown
    await state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

# Use in endpoints
@app.get("/external")
async def call_external():
    response = await state.http_client.get("https://api.example.com/data")
    return response.json()
```

---

## 6. Async Database Access

### SQLAlchemy Async

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

---

## 7. Background Tasks

### Simple Background Task

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # This runs after response is sent
    time.sleep(5)  # Simulate sending
    print(f"Sent to {email}")

@app.post("/users")
def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    # Create user...
    background_tasks.add_task(send_email, user.email, "Welcome!")
    return {"message": "User created"}
```

### Async Background Task

```python
async def send_notification(user_id: int):
    async with httpx.AsyncClient() as client:
        await client.post(f"https://notify.example.com/{user_id}")

@app.post("/users")
async def create_user(user: UserCreate, background_tasks: BackgroundTasks):
    # Note: background_tasks work with async functions too
    background_tasks.add_task(send_notification, user.id)
    return {"message": "User created"}
```

---

## 8. Common Pitfalls

### ❌ Mixing sync and async incorrectly

```python
# BAD: Blocking call in async function
@app.get("/bad")
async def bad_endpoint():
    response = requests.get(url)  # Blocks entire event loop!
    return response.json()

# GOOD: Use async client
@app.get("/good")
async def good_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### ❌ Creating client per request

```python
# BAD: New client every request (expensive)
@app.get("/bad")
async def bad():
    client = httpx.AsyncClient()
    response = await client.get(url)
    await client.aclose()
    return response.json()

# GOOD: Shared client with lifespan
```

### ❌ Forgetting await

```python
# BAD: Returns coroutine object, not result
@app.get("/bad")
async def bad():
    return fetch_data()  # Missing await!

# GOOD
@app.get("/good")
async def good():
    return await fetch_data()
```

---

## 9. When to Use Async

### Use async for:

- ✅ HTTP API calls
- ✅ Database queries (with async driver)
- ✅ File I/O (with aiofiles)
- ✅ WebSocket connections
- ✅ Multiple concurrent I/O operations

### Use sync for:

- ❌ CPU-intensive computation
- ❌ Simple endpoints with no I/O
- ❌ Libraries without async support

---

## 10. Timeouts

```python
import asyncio
import httpx

async def fetch_with_timeout(url: str, timeout: float = 5.0):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Upstream timeout")

# Or with asyncio.timeout (Python 3.11+)
async def fetch_with_asyncio_timeout(url: str):
    async with asyncio.timeout(5.0):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

---

## Quick Reference

### Concurrent Requests

```python
results = await asyncio.gather(task1, task2, task3)
```

### Limit Concurrency

```python
sem = asyncio.Semaphore(10)
async with sem:
    await operation()
```

### Background Task

```python
background_tasks.add_task(func, arg1, arg2)
```

### httpx Client

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

---

## Summary

You've learned:

1. **Async basics** — async/await, when to use
2. **httpx** — async HTTP client
3. **Concurrent requests** — asyncio.gather
4. **Semaphores** — limiting concurrency
5. **Background tasks** — post-response processing
6. **Pitfalls** — blocking calls, missing awaits

**API Patterns module complete!**

You now have the foundation for building production FastAPI applications.
