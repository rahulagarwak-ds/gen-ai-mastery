# Chapter 4: API Error Handling

> _"Good error handling is invisible to users — until they need it."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- FastAPI exception handling
- Custom exception classes
- Exception handlers
- Consistent error responses
- Validation error formatting
- Logging errors

---

## 1. Default FastAPI Errors

FastAPI provides automatic error responses:

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]
```

Response:

```json
{
  "detail": "Item not found"
}
```

---

## 2. HTTPException Details

```python
from fastapi import HTTPException, status

# With status constant
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found"
)

# With headers
raise HTTPException(
    status_code=401,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"}
)

# With structured detail
raise HTTPException(
    status_code=400,
    detail={
        "error": "VALIDATION_ERROR",
        "message": "Invalid input",
        "fields": ["email", "password"]
    }
)
```

---

## 3. Custom Exception Classes

```python
# exceptions.py
class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.status_code = status_code

class NotFoundError(AppException):
    def __init__(self, resource: str, resource_id: str | int):
        super().__init__(
            message=f"{resource} '{resource_id}' not found",
            code="NOT_FOUND",
            status_code=404
        )

class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )

class ForbiddenError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403
        )

class ValidationError(AppException):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422
        )
        self.field = field
```

---

## 4. Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
        }
    )

# Now you can raise anywhere:
@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = db.get(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user
```

---

## 5. Consistent Error Response Model

```python
from pydantic import BaseModel
from typing import Any

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[dict[str, Any]] | None = None
    request_id: str | None = None

# Register response model in docs
@app.get(
    "/users/{user_id}",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    }
)
def get_user(user_id: int):
    ...
```

---

## 6. Handling Pydantic Validation Errors

Override default validation error handler:

```python
from fastapi.exceptions import RequestValidationError
from fastapi import Request

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"][1:]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": errors,
        }
    )
```

Output:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Request validation failed",
  "details": [
    {
      "field": "email",
      "message": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 7. Global Exception Handler

Catch-all for unexpected errors:

```python
import logging
import traceback

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full traceback
    logger.error(
        f"Unhandled exception: {exc}\n{traceback.format_exc()}"
    )

    # Return generic error to client (don't expose internals)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
        }
    )
```

---

## 8. Request ID for Tracing

```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Include in error responses
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "request_id": request_id_var.get(),
        }
    )
```

---

## 9. Error Logging

```python
import logging
from fastapi import Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    # Log 4xx as warnings, 5xx as errors
    log_func = logger.warning if exc.status_code < 500 else logger.error

    log_func(
        f"[{request_id_var.get()}] {exc.code}: {exc.message} "
        f"path={request.url.path}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "message": exc.message}
    )
```

---

## 10. Complete Error Setup

```python
# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .exceptions import AppException

app = FastAPI()

# Custom exceptions
@app.exception_handler(AppException)
async def handle_app_exception(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.code, "message": exc.message}
    )

# Validation errors
@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": [
                {"field": ".".join(map(str, e["loc"][1:])), "message": e["msg"]}
                for e in exc.errors()
            ]
        }
    )

# Catch-all
@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "Something went wrong"}
    )
```

---

## Quick Reference

### Raise Errors

```python
raise HTTPException(status_code=404, detail="Not found")
raise NotFoundError("User", user_id)  # Custom
```

### Register Handler

```python
@app.exception_handler(MyException)
async def handler(request, exc):
    return JSONResponse(...)
```

### Error Response

```json
{
    "error": "ERROR_CODE",
    "message": "Human readable message",
    "details": [...],
    "request_id": "uuid"
}
```

---

## Summary

You've learned:

1. **HTTPException** — built-in errors
2. **Custom exceptions** — typed error classes
3. **Exception handlers** — consistent responses
4. **Validation errors** — formatting Pydantic errors
5. **Logging** — tracking errors
6. **Request ID** — tracing errors

Next chapter: Async Patterns — concurrent requests and async I/O.
