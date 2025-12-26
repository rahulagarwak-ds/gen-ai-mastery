# Chapter 1: AsyncIO Deep-Dive — Concurrency Done Right

> _"Async isn't faster. It's more efficient with waiting."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- How asyncio actually works under the hood
- Event loops and their lifecycle
- Coroutines, tasks, and futures
- Task groups and structured concurrency
- Async context managers and iterators
- Common patterns and pitfalls

---

## 1. The Mental Model

### Sync vs Async

```python
# SYNC: One thing at a time, blocking
def sync_fetch():
    result1 = fetch_url_1()  # Wait 2s
    result2 = fetch_url_2()  # Wait 2s
    return result1, result2  # Total: 4 seconds

# ASYNC: Multiple things waiting together
async def async_fetch():
    result1, result2 = await asyncio.gather(
        fetch_url_1(),  # Start
        fetch_url_2()   # Start simultaneously
    )
    return result1, result2  # Total: ~2 seconds
```

### When Async Helps

```
✅ Good for async:           ❌ Bad for async:
- Network I/O (APIs, DBs)    - CPU-bound work
- File I/O                   - Heavy computation
- Many concurrent waits      - Simple scripts
- WebSockets                 - GIL-bound operations
```

---

## 2. Event Loop Internals

### What the Event Loop Does

```
┌─────────────────────────────────────────────────────────┐
│                     EVENT LOOP                          │
│                                                         │
│   ┌──────┐    ┌──────┐    ┌──────┐                     │
│   │Task 1│    │Task 2│    │Task 3│                     │
│   └──┬───┘    └──┬───┘    └──┬───┘                     │
│      │           │           │                          │
│      ▼           ▼           ▼                          │
│   [await]     [await]     [running]                     │
│                                                         │
│   The loop runs one task until it awaits,               │
│   then switches to another ready task.                  │
└─────────────────────────────────────────────────────────┘
```

### Creating and Running the Loop

```python
import asyncio

# Modern way (Python 3.10+)
async def main():
    print("Hello, async!")

asyncio.run(main())  # Creates loop, runs, cleans up

# Manual control (rarely needed)
loop = asyncio.new_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()
```

### Getting the Current Loop

```python
async def example():
    loop = asyncio.get_running_loop()
    print(f"Running on: {loop}")
```

---

## 3. Coroutines, Tasks, and Futures

### Coroutine

A coroutine is a function defined with `async def`:

```python
async def fetch_data():
    await asyncio.sleep(1)
    return "data"

# Calling it returns a coroutine OBJECT (not the result!)
coro = fetch_data()  # <coroutine object>

# You must await it to get the result
result = await coro  # "data"
```

### Task

A Task wraps a coroutine and schedules it on the loop:

```python
async def main():
    # Create task - starts running immediately
    task = asyncio.create_task(fetch_data())

    # Do other work while task runs
    print("Task is running...")

    # Wait for result when needed
    result = await task
    print(f"Got: {result}")
```

### Task vs Await

```python
# Sequential (slow)
result1 = await fetch_url_1()  # Wait 2s
result2 = await fetch_url_2()  # Wait 2s
# Total: 4s

# Concurrent with tasks (fast)
task1 = asyncio.create_task(fetch_url_1())
task2 = asyncio.create_task(fetch_url_2())
result1 = await task1
result2 = await task2
# Total: 2s

# Even better with gather
results = await asyncio.gather(fetch_url_1(), fetch_url_2())
# Total: 2s
```

### Future

Low-level primitive (rarely use directly):

```python
async def set_result_later(future: asyncio.Future):
    await asyncio.sleep(1)
    future.set_result("done!")

async def main():
    future = asyncio.get_running_loop().create_future()
    asyncio.create_task(set_result_later(future))
    result = await future  # Waits for set_result
```

---

## 4. asyncio.gather vs create_task

### asyncio.gather

```python
# Run multiple coroutines concurrently
results = await asyncio.gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3)
)
# results is a list in the same order

# With error handling
results = await asyncio.gather(
    *coroutines,
    return_exceptions=True  # Don't fail on first exception
)
```

### asyncio.create_task

```python
# More control over individual tasks
task1 = asyncio.create_task(fetch_user(1))
task2 = asyncio.create_task(fetch_user(2))

# Can cancel individual tasks
task1.cancel()

# Can check status
if task2.done():
    result = task2.result()
```

### When to Use Which

| Use Case                      | Tool          |
| ----------------------------- | ------------- |
| Run N things, get all results | `gather`      |
| Fire and forget               | `create_task` |
| Need to cancel individually   | `create_task` |
| Complex coordination          | `TaskGroup`   |

---

## 5. Task Groups (Python 3.11+)

### Structured Concurrency

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch_user(1))
        task2 = tg.create_task(fetch_user(2))
        task3 = tg.create_task(fetch_user(3))

    # All tasks guaranteed complete here
    print(task1.result(), task2.result(), task3.result())
```

### Exception Handling

```python
async def might_fail(n: int):
    if n == 2:
        raise ValueError("oops")
    return n

async def main():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(might_fail(1))
            tg.create_task(might_fail(2))  # Raises!
            tg.create_task(might_fail(3))
    except* ValueError as eg:
        for exc in eg.exceptions:
            print(f"Caught: {exc}")
```

### TaskGroup vs gather

| Feature            | TaskGroup      | gather       |
| ------------------ | -------------- | ------------ |
| Python version     | 3.11+          | 3.4+         |
| Cancel on error    | Yes (all)      | Optional     |
| Exception handling | ExceptionGroup | First or all |
| Structured         | Yes            | No           |

---

## 6. Async Context Managers

### Creating Async Context Managers

```python
class AsyncConnection:
    async def __aenter__(self):
        print("Connecting...")
        await asyncio.sleep(0.1)  # Simulate connection
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting...")
        await asyncio.sleep(0.1)
        return False

async def main():
    async with AsyncConnection() as conn:
        print("Connected!")
```

### Using contextlib

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_timer(name: str):
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        print(f"{name} took {elapsed:.2f}s")

async def main():
    async with async_timer("fetch"):
        await fetch_data()
```

---

## 7. Async Iterators

### Creating Async Iterators

```python
class AsyncCounter:
    def __init__(self, stop: int):
        self.stop = stop
        self.current = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.current >= self.stop:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.current += 1
        return self.current

async def main():
    async for num in AsyncCounter(5):
        print(num)
```

### Async Generators

```python
async def async_range(stop: int):
    for i in range(stop):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_range(5):
        print(num)
```

### async for with real use cases

```python
# Streaming API responses
async for chunk in stream_llm_response(prompt):
    print(chunk, end="")

# Processing database rows
async for row in db.execute("SELECT * FROM users"):
    process(row)
```

---

## 8. Timeouts and Cancellation

### Timeouts

```python
# Simple timeout
try:
    result = await asyncio.wait_for(
        slow_operation(),
        timeout=5.0
    )
except asyncio.TimeoutError:
    print("Operation timed out!")

# Timeout context (Python 3.11+)
async with asyncio.timeout(5.0):
    result = await slow_operation()
```

### Cancellation

```python
async def long_task():
    try:
        while True:
            await asyncio.sleep(1)
            print("Working...")
    except asyncio.CancelledError:
        print("Cancelled! Cleaning up...")
        raise  # Re-raise to confirm cancellation

async def main():
    task = asyncio.create_task(long_task())
    await asyncio.sleep(3)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")
```

---

## 9. Common Patterns

### Semaphore for Rate Limiting

```python
async def fetch_with_limit(url: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        return await fetch(url)

async def main():
    # Max 10 concurrent requests
    sem = asyncio.Semaphore(10)
    urls = [f"https://api.com/{i}" for i in range(100)]

    tasks = [fetch_with_limit(url, sem) for url in urls]
    results = await asyncio.gather(*tasks)
```

### Producer-Consumer with Queue

```python
async def producer(queue: asyncio.Queue):
    for i in range(10):
        await queue.put(i)
        print(f"Produced: {i}")
    await queue.put(None)  # Sentinel

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        await asyncio.sleep(0.5)

async def main():
    queue = asyncio.Queue()
    await asyncio.gather(producer(queue), consumer(queue))
```

### Running Sync Code in Async

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def blocking_io():
    import time
    time.sleep(2)
    return "done"

async def main():
    loop = asyncio.get_running_loop()

    # Run in thread pool
    result = await loop.run_in_executor(None, blocking_io)

    # Or with custom executor
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = await loop.run_in_executor(pool, blocking_io)
```

---

## 10. Common Pitfalls

### ❌ Blocking the Event Loop

```python
# BAD: Blocks entire loop!
async def bad():
    import time
    time.sleep(5)  # BLOCKS!

# GOOD: Async sleep
async def good():
    await asyncio.sleep(5)

# GOOD: Run blocking in executor
async def also_good():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, time.sleep, 5)
```

### ❌ Forgetting to await

```python
# BAD: Creates coroutine but doesn't run it
async def bad():
    fetch_data()  # Just creates coroutine object!

# GOOD
async def good():
    await fetch_data()
```

### ❌ Creating Tasks Outside Async Context

```python
# BAD: No running loop
task = asyncio.create_task(coro())  # RuntimeError!

# GOOD: Inside async function
async def main():
    task = asyncio.create_task(coro())
```

---

## Quick Reference

### Run async code

```python
asyncio.run(main())
```

### Concurrent execution

```python
results = await asyncio.gather(coro1(), coro2(), coro3())
```

### Task groups (3.11+)

```python
async with asyncio.TaskGroup() as tg:
    task = tg.create_task(coro())
```

### Timeouts

```python
await asyncio.wait_for(coro(), timeout=5.0)
```

### Semaphore

```python
async with asyncio.Semaphore(10):
    await limited_operation()
```

---

## Summary

You've learned:

1. **Event loop** — how async scheduling works
2. **Coroutines & Tasks** — creating and managing
3. **gather** — concurrent execution
4. **TaskGroups** — structured concurrency
5. **Async context managers** — resource management
6. **Async iterators** — streaming data
7. **Patterns** — semaphores, queues, executors
8. **Pitfalls** — blocking, forgetting await

Next chapter: Database — async ORM with SQLModel.
