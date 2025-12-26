# Chapter 9: Error Handling

> _"Software doesn't fail gracefully by accident. Every recovery path is a conscious decision."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Exception hierarchy and types
- try/except/else/finally patterns
- Raising and re-raising exceptions
- Custom exception classes
- Context managers
- Defensive programming strategies
- Logging errors properly

---

## Prerequisites

- Chapters 1-8: All previous content

---

## 1. Exception Basics

### 1.1 The Exception Hierarchy

```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ValueError
    ├── TypeError
    ├── KeyError
    ├── IndexError
    ├── AttributeError
    ├── FileNotFoundError
    ├── IOError
    └── ... many more
```

**Rule:** Catch `Exception`, not `BaseException`. Let `SystemExit` and `KeyboardInterrupt` pass through.

### 1.2 Basic try/except

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
```

### 1.3 Catching Multiple Exceptions

```python
try:
    data = json.loads(user_input)
    value = data["key"]
except json.JSONDecodeError:
    print("Invalid JSON")
except KeyError:
    print("Missing 'key' field")

# Or combined
except (json.JSONDecodeError, KeyError) as e:
    print(f"Data error: {e}")
```

### 1.4 The `else` Clause

Runs only if NO exception occurred.

```python
try:
    result = process(data)
except ValueError:
    print("Invalid data")
else:
    # Only runs on success
    save_result(result)
    print("Saved successfully")
```

### 1.5 The `finally` Clause

ALWAYS runs — cleanup code.

```python
file = None
try:
    file = open("data.txt")
    content = file.read()
except FileNotFoundError:
    print("File not found")
finally:
    if file:
        file.close()  # Always runs, even if exception
```

---

## 2. Raising Exceptions

### 2.1 Basic Raise

```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# With message
raise ValueError("Detailed error message")

# Without message
raise ValueError
```

### 2.2 Re-raising Exceptions

```python
try:
    risky_operation()
except ValueError:
    log_error("Something went wrong")
    raise  # Re-raise the same exception

# Chain exceptions
try:
    parse_config()
except KeyError as e:
    raise ConfigError("Invalid config") from e
```

### 2.3 Exception Chaining

```python
class ConfigError(Exception):
    pass

try:
    data = load_json(path)
    validate(data)
except (FileNotFoundError, json.JSONDecodeError) as e:
    # Chain to show original cause
    raise ConfigError(f"Failed to load config: {path}") from e
```

---

## 3. Custom Exceptions

### 3.1 Basic Custom Exception

```python
class ValidationError(Exception):
    """Raised when data validation fails."""
    pass

class NotFoundError(Exception):
    """Raised when a resource is not found."""
    pass

# Usage
raise ValidationError("Email format is invalid")
```

### 3.2 Custom Exception with Data

```python
class APIError(Exception):
    """Error from external API."""

    def __init__(self, message: str, status_code: int, response: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response or {}

try:
    call_api()
except APIError as e:
    print(f"API failed: {e.status_code}")
    print(f"Response: {e.response}")
```

### 3.3 Exception Hierarchy

```python
class ApplicationError(Exception):
    """Base exception for application."""
    pass

class ValidationError(ApplicationError):
    """Data validation failed."""
    pass

class AuthenticationError(ApplicationError):
    """Authentication failed."""
    pass

class AuthorizationError(ApplicationError):
    """Authorization failed."""
    pass

# Catch all application errors
try:
    do_something()
except ApplicationError as e:
    handle_application_error(e)
```

---

## 4. Context Managers

### 4.1 Using `with` Statement

```python
# Files are automatically closed
with open("data.txt") as f:
    content = f.read()
# f is closed here, even if exception occurred

# Multiple resources
with open("input.txt") as infile, open("output.txt", "w") as outfile:
    outfile.write(infile.read())
```

### 4.2 Creating Context Managers (Class)

```python
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"Elapsed: {self.elapsed:.4f}s")
        return False  # Don't suppress exceptions

with Timer() as t:
    # Do something
    time.sleep(1)
# Prints: "Elapsed: 1.0012s"
```

### 4.3 Creating Context Managers (contextlib)

```python
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.perf_counter()
    yield  # Code inside 'with' runs here
    end = time.perf_counter()
    print(f"Elapsed: {end - start:.4f}s")

with timer():
    time.sleep(1)
```

### 4.4 Practical Context Managers

```python
from contextlib import contextmanager

@contextmanager
def temp_directory():
    """Create a temp directory, clean up after."""
    import tempfile
    import shutil

    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)

with temp_directory() as tmp:
    # Use tmp directory
    pass
# Directory is automatically deleted
```

---

## 5. Defensive Programming

### 5.1 Guard Clauses

```python
def process_user(user):
    # Guard clauses at the top
    if user is None:
        raise ValueError("User cannot be None")
    if not user.is_active:
        raise ValueError("User must be active")
    if not user.has_permission("process"):
        raise PermissionError("User lacks permission")

    # Main logic (flat, not nested)
    return do_processing(user)
```

### 5.2 Assert for Development

```python
def calculate_discount(price: float, rate: float) -> float:
    # Development checks (disabled in production with -O)
    assert price >= 0, "Price must be non-negative"
    assert 0 <= rate <= 1, "Rate must be between 0 and 1"

    return price * (1 - rate)
```

**Warning:** Don't use assert for runtime checks! Use exceptions.

### 5.3 EAFP vs LBYL

```python
# LBYL (Look Before You Leap) — check first
if "key" in data:
    value = data["key"]
else:
    value = default

# EAFP (Easier to Ask Forgiveness) — try and catch (Pythonic)
try:
    value = data["key"]
except KeyError:
    value = default

# Even better: use .get()
value = data.get("key", default)
```

---

## 6. Logging Errors

### 6.1 Setup Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```

### 6.2 Log Exceptions

```python
try:
    risky_operation()
except Exception:
    logger.exception("Operation failed")  # Includes traceback
    raise

# Or with specific handling
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except IOError as e:
    logger.error(f"IO error: {e}", exc_info=True)  # Include traceback
```

### 6.3 Structured Logging Pattern

```python
try:
    result = process_order(order_id)
except OrderError as e:
    logger.error(
        "Order processing failed",
        extra={
            "order_id": order_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
        }
    )
    raise
```

---

## 7. Common Patterns

### 7.1 Retry Pattern

```python
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator
```

### 7.2 Fallback Pattern

```python
def get_data():
    try:
        return fetch_from_api()
    except APIError:
        logger.warning("API failed, using cache")
        return get_from_cache()
```

### 7.3 Cleanup Pattern

```python
resource = None
try:
    resource = acquire_resource()
    use_resource(resource)
finally:
    if resource:
        release_resource(resource)
```

---

## ⚠️ Common Mistakes

### Bare Except

```python
# WRONG — catches everything including KeyboardInterrupt
try:
    do_something()
except:
    pass

# RIGHT — catch Exception
try:
    do_something()
except Exception as e:
    logger.error(f"Error: {e}")
```

### Silent Failures

```python
# WRONG — errors disappear
try:
    do_something()
except Exception:
    pass  # Silent failure is dangerous

# RIGHT — at least log
try:
    do_something()
except Exception as e:
    logger.error(f"Failed: {e}")
    # Then decide: re-raise, return default, etc.
```

---

## Quick Reference

### Exception Handling

```python
try:
    risky_code()
except SpecificError as e:
    handle_error(e)
except (Error1, Error2):
    handle_multiple()
else:
    on_success()
finally:
    cleanup()
```

### Context Manager

```python
@contextmanager
def my_context():
    setup()
    try:
        yield resource
    finally:
        teardown()
```

### Custom Exception

```python
class MyError(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code
```

---

## Summary

You've learned:

1. **Exception hierarchy** — know what to catch
2. **try/except/else/finally** — full control flow
3. **Custom exceptions** — application-specific errors
4. **Context managers** — guaranteed cleanup
5. **Defensive programming** — guard clauses, EAFP
6. **Logging** — proper error tracking
7. **Patterns** — retry, fallback, cleanup

Next chapter: Iterators & Generators — lazy evaluation and memory efficiency.
