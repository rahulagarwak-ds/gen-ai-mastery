# Mini Project: Exception Hierarchy & Context Managers

## 🎯 Objective

Build a production-ready exception hierarchy and reusable context managers for application error handling.

---

## 📋 Part 1: Application Exception Hierarchy

### Base Exception

```python
class ApplicationError(Exception):
    """
    Base exception for all application errors.

    Features:
        - Store error code
        - to_dict() method for API responses
    """
    def __init__(self, message: str, code: str | None = None):
        pass

    def to_dict(self) -> dict:
        """Return {"error": code, "message": message}"""
        pass
```

### Domain Exceptions

```python
class ValidationError(ApplicationError):
    """
    Input validation failed.
    Add: field attribute to identify which field failed.
    """
    pass

class NotFoundError(ApplicationError):
    """
    Resource not found.

    Usage:
        raise NotFoundError("User", 123)
        # Message: "User '123' not found"
    """
    pass

class AuthenticationError(ApplicationError):
    """Authentication failed."""
    pass

class AuthorizationError(ApplicationError):
    """
    User lacks permission.

    Usage:
        raise AuthorizationError("delete", "document")
        # Message: "Not authorized to delete on document"
    """
    pass

class RateLimitError(ApplicationError):
    """
    Rate limit exceeded.
    Add: retry_after attribute (seconds).
    """
    pass
```

### External Service Exceptions

```python
class ExternalServiceError(ApplicationError):
    """Base for external service errors."""
    pass

class APIError(ExternalServiceError):
    """
    HTTP API error.
    Add: status_code, response_body attributes.
    """
    pass

class LLMError(ExternalServiceError):
    """LLM API error. Add: provider, model attributes."""
    pass

class LLMRateLimitError(LLMError):
    """LLM rate limit. Add: retry_after attribute."""
    pass

class LLMContextLengthError(LLMError):
    """Context too long. Add: max_tokens, actual_tokens attributes."""
    pass
```

---

## 📋 Part 2: Context Managers

### Timer Context Manager

```python
@contextmanager
def timer(name: str = "Block"):
    """
    Time a code block.

    Usage:
        with timer("Database query"):
            # ... code ...
        # Prints: "Database query took 0.123s"
    """
    pass
```

### Suppress and Log

```python
@contextmanager
def suppress_and_log(*exceptions, logger=None):
    """
    Suppress exceptions but log them.

    Usage:
        with suppress_and_log(ValueError, KeyError):
            raise ValueError("oops")
        # Prints/logs: "Suppressed ValueError: oops"
        # Continues execution
    """
    pass
```

### Temp Directory

```python
@contextmanager
def temp_directory():
    """
    Create temp directory, auto-cleanup after.

    Usage:
        with temp_directory() as path:
            (path / "file.txt").write_text("hello")
        # Directory deleted after block
    """
    pass
```

### Atomic Write

```python
@contextmanager
def atomic_write(filepath: str | Path, mode: str = "w"):
    """
    Write to file atomically (write to temp, then rename).
    If error occurs, original file is unchanged.

    Usage:
        with atomic_write("config.json") as f:
            f.write(json.dumps(data))
        # File only updated if write completes successfully
    """
    pass
```

---

## ✅ Test Cases

```python
# Exception tests
try:
    raise NotFoundError("User", 123)
except ApplicationError as e:
    assert e.to_dict() == {"error": "NOT_FOUND", "message": "User '123' not found"}

try:
    raise ValidationError("Invalid email", field="email")
except ValidationError as e:
    assert e.field == "email"

# Context manager tests
with timer("Test"):
    time.sleep(0.1)
# Should print: "Test took 0.10XXs"

with suppress_and_log(ValueError):
    raise ValueError("ignored")
print("This runs!")  # Execution continues

with temp_directory() as tmp:
    file = tmp / "test.txt"
    file.write_text("hello")
    assert file.exists()
assert not tmp.exists()  # Cleaned up
```

---

## 🏆 Bonus Challenges

1. Add `@contextmanager` for database transactions with rollback on error
2. Add `ExceptionGroup` handling for Python 3.11+
3. Add exception logging with structured fields (JSON-friendly)

---

## 📁 Deliverable

Create `exceptions.py` with all exceptions and context managers.

**Time estimate:** 45-60 minutes
