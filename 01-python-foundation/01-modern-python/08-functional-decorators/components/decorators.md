# Mini Project: Production Decorators Module

## 🎯 Objective

Build a collection of production-ready decorators that you'll use throughout your Gen AI engineering work.

---

## 📋 Requirements

### 1. Timer Decorator

```python
def timer(func=None, *, logger=None):
    """
    Log execution time of a function.

    Usage:
        @timer
        def my_func(): ...

        @timer(logger=my_logger)
        def my_func(): ...

    Should print/log: "my_func took 0.1234s"
    """
    pass
```

### 2. Retry Decorator

```python
def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry a function on failure with exponential backoff.

    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch

    Usage:
        @retry(max_attempts=3, delay=1.0)
        def call_api(): ...
    """
    pass
```

### 3. Log Calls Decorator

```python
def log_calls(logger=None, level=logging.INFO):
    """
    Log function calls with arguments and return values.

    Should log:
        - Calling function_name(arg1, arg2, kwarg=value)
        - function_name returned result
        - OR function_name raised ErrorType: message
    """
    pass
```

### 4. Rate Limiter Decorator

```python
def rate_limit(max_calls: int, period: float):
    """
    Limit function calls to max_calls per period seconds.
    Block/sleep if limit is exceeded.

    Usage:
        @rate_limit(max_calls=10, period=60)  # 10 calls per minute
        def call_api(): ...
    """
    pass
```

### 5. Memoize with TTL

```python
def memoize_with_ttl(ttl_seconds: float = 300):
    """
    Cache function results with time-to-live expiration.

    Args:
        ttl_seconds: How long to keep cached values

    Should support:
        func.cache_clear()  - Clear the cache
        func.cache_info()   - Return cache stats
    """
    pass
```

---

## ✅ Test Cases

```python
import time

# Timer test
@timer
def slow_func():
    time.sleep(0.5)
    return "done"

slow_func()  # Should print: "slow_func took 0.50XXs"

# Retry test
attempt = 0

@retry(max_attempts=3, delay=0.1)
def flaky_func():
    global attempt
    attempt += 1
    if attempt < 3:
        raise ValueError("fail")
    return "success"

assert flaky_func() == "success"
assert attempt == 3

# Rate limit test
@rate_limit(max_calls=3, period=1)
def limited_func(n):
    return n

start = time.time()
for i in range(5):
    limited_func(i)
elapsed = time.time() - start
assert elapsed >= 1.0  # Should have waited due to rate limit

# TTL cache test
@memoize_with_ttl(ttl_seconds=1)
def cached_func(x):
    return x * 2

cached_func(5)  # Computes
cached_func(5)  # From cache
time.sleep(1.5)
cached_func(5)  # Expired, recomputes
```

---

## 🏆 Bonus Challenges

1. Add `@validate_args(**validators)` that validates function arguments
2. Add `@deprecated(message)` that warns when function is called
3. Add `@timeout(seconds)` that raises TimeoutError if function takes too long

---

## 📁 Deliverable

Create `decorators.py` with all decorators, using `@functools.wraps` to preserve metadata.

**Time estimate:** 60-90 minutes

---

## 💡 Hints

<details>
<summary>Hint 1: Decorator with optional arguments</summary>

```python
def decorator(func=None, *, kwarg=default):
    def actual_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper

    if func is not None:
        return actual_decorator(func)
    return actual_decorator
```

</details>

<details>
<summary>Hint 2: Rate Limiter</summary>

Use a `deque` to track call timestamps. Remove old timestamps outside the window.

</details>
