# Workout: AsyncIO Deep-Dive

## Setup

```bash
uv add aiohttp httpx
```

---

## Drill 1: Basic Async Function 🟢

**Task:** Create and run a simple async function

```python
import asyncio

async def greet(name: str) -> str:
    await asyncio.sleep(0.5)
    return f"Hello, {name}!"

# Run it using asyncio.run()
# Print the result

```

---

## Drill 2: Concurrent with gather 🟢

**Task:** Run multiple coroutines concurrently

```python
import asyncio

async def fetch(id: int) -> dict:
    await asyncio.sleep(1)
    return {"id": id, "data": f"result_{id}"}

async def main():
    # Fetch IDs 1, 2, 3 concurrently
    # Should take ~1 second, not 3
    pass

import time
start = time.time()
asyncio.run(main())
print(f"Took: {time.time() - start:.2f}s")  # Should be ~1s
```

---

## Drill 3: create_task 🟡

**Task:** Create tasks and manage them

```python
import asyncio

async def worker(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    # Create 3 tasks with different delays
    # Print as each completes
    pass
```

---

## Drill 4: TaskGroup 🟡

**Task:** Use TaskGroup for structured concurrency (Python 3.11+)

```python
import asyncio

async def process(n: int) -> int:
    await asyncio.sleep(0.5)
    return n * 2

async def main():
    # Use TaskGroup to process numbers 1-5
    # Collect all results
    pass

asyncio.run(main())
```

---

## Drill 5: Timeout 🟢

**Task:** Handle a slow operation with timeout

```python
import asyncio

async def slow_operation():
    await asyncio.sleep(10)
    return "done"

async def main():
    # Set 2 second timeout
    # Handle TimeoutError gracefully
    pass
```

---

## Drill 6: Semaphore Rate Limiting 🟡

**Task:** Limit concurrent operations

```python
import asyncio

async def api_call(id: int, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        print(f"Starting {id}")
        await asyncio.sleep(0.5)
        print(f"Done {id}")
        return {"id": id}

async def main():
    # Make 20 API calls but max 5 concurrent
    pass
```

---

## Drill 7: Async Context Manager 🟡

**Task:** Create a custom async context manager

```python
from contextlib import asynccontextmanager
import asyncio

@asynccontextmanager
async def timed_operation(name: str):
    """Track operation time."""
    # Record start time
    # Yield
    # Print elapsed time
    pass

async def main():
    async with timed_operation("fetch"):
        await asyncio.sleep(1.5)
    # Should print "fetch took 1.50s" or similar
```

---

## Drill 8: Async Generator 🟡

**Task:** Create a streaming data source

```python
import asyncio

async def stream_numbers(count: int, delay: float = 0.1):
    """Yield numbers with delay."""
    pass

async def main():
    async for num in stream_numbers(10):
        print(num)
```

---

## Drill 9: Producer-Consumer Queue 🔴

**Task:** Implement producer-consumer pattern

```python
import asyncio

async def producer(queue: asyncio.Queue, items: list):
    """Put items in queue."""
    pass

async def consumer(queue: asyncio.Queue, name: str):
    """Take and process items from queue."""
    pass

async def main():
    queue = asyncio.Queue()
    items = list(range(10))

    # Run 1 producer and 3 consumers
    pass
```

---

## Drill 10: Run Blocking Code 🔴

**Task:** Run sync blocking code without blocking the loop

```python
import asyncio
import time

def blocking_io_operation(seconds: int) -> str:
    time.sleep(seconds)  # Simulates blocking I/O
    return f"Slept {seconds}s"

async def main():
    # Run blocking_io_operation(2) without blocking
    # Use run_in_executor
    pass

start = time.time()
asyncio.run(main())
# Should not block other tasks
```

---

## Self-Check

- [ ] Understand difference between coroutine and task
- [ ] Can use gather for concurrent execution
- [ ] Can use TaskGroup for structured concurrency
- [ ] Can implement timeouts and cancellation
- [ ] Can use semaphores for rate limiting
- [ ] Can create async context managers and generators
- [ ] Know how to run blocking code in async context
