# Chapter 2: Pydantic Models for APIs

> _"If it doesn't validate, it doesn't pass."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Request and response model patterns
- Field validation and constraints
- Custom validators
- Nested models
- Model inheritance
- Serialization options

---

## 1. Request Models

### Basic Create Model

```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int | None = Field(None, ge=0, le=150)
```

### Update Model (Partial)

```python
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    age: int | None = None

    # At least one field required
    @model_validator(mode="after")
    def check_at_least_one(self):
        if not any([self.name, self.email, self.age is not None]):
            raise ValueError("At least one field must be provided")
        return self
```

### Pattern: Create vs Update

```python
# Base with shared fields
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Create includes password
class UserCreate(UserBase):
    password: str

# Update makes everything optional
class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
```

---

## 2. Response Models

### Basic Response

```python
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    # Never expose password!
```

### With Computed Fields

```python
from pydantic import computed_field

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

### List Response with Pagination

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=(total + page_size - 1) // page_size
        )

# Usage
@app.get("/users", response_model=PaginatedResponse[UserResponse])
def list_users(page: int = 1, page_size: int = 10):
    ...
```

---

## 3. Field Validation

### Built-in Constraints

```python
from pydantic import Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    sku: str = Field(..., pattern=r"^[A-Z]{3}-\d{4}$")
    tags: list[str] = Field(default=[], max_length=10)
```

### Common Constraints

| Type      | Constraints                     |
| --------- | ------------------------------- |
| str       | min_length, max_length, pattern |
| int/float | gt, ge, lt, le, multiple_of     |
| list      | min_length, max_length          |
| Any       | default, default_factory        |

---

## 4. Custom Validators

### Field Validator

```python
from pydantic import field_validator

class User(BaseModel):
    email: str
    username: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v
```

### Model Validator (Cross-field)

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be after start_date")
        return self
```

---

## 5. Nested Models

```python
class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str

class Company(BaseModel):
    name: str
    address: Address

class UserWithCompany(BaseModel):
    id: int
    name: str
    company: Company | None = None

# Usage in request
user_data = {
    "id": 1,
    "name": "Alice",
    "company": {
        "name": "Acme Inc",
        "address": {
            "street": "123 Main St",
            "city": "NYC",
            "country": "USA",
            "zip_code": "10001"
        }
    }
}
```

---

## 6. Enums and Literals

```python
from enum import Enum
from typing import Literal

class Status(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"

class Order(BaseModel):
    id: int
    status: Status
    priority: Literal["low", "medium", "high"]

# Both work in requests
# {"status": "active", "priority": "high"}
```

---

## 7. Serialization Control

### Exclude Fields

```python
class UserDB(BaseModel):
    id: int
    name: str
    password_hash: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 1, "name": "Alice"}]
        }
    }

@app.get("/users/{id}")
def get_user(id: int):
    user = get_user_from_db(id)
    return user.model_dump(exclude={"password_hash"})
```

### Include Only

```python
# Only specific fields
user.model_dump(include={"id", "name"})
```

### Alias for JSON Keys

```python
class Event(BaseModel):
    event_type: str = Field(..., alias="eventType")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = {"populate_by_name": True}

# Accepts both:
# {"eventType": "click"} or {"event_type": "click"}
```

---

## 8. Example Patterns

### API Error Response

```python
class ErrorDetail(BaseModel):
    field: str | None = None
    message: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: list[ErrorDetail] = []
```

### Flexible Input

```python
class SearchQuery(BaseModel):
    q: str
    filters: dict[str, str | int | bool] = {}
    sort_by: str = "created_at"
    order: Literal["asc", "desc"] = "desc"
```

---

## Quick Reference

### Model Patterns

```python
class ItemBase(BaseModel):     # Shared fields
    name: str

class ItemCreate(ItemBase):    # Create-specific
    password: str

class ItemUpdate(BaseModel):   # All optional
    name: str | None = None

class ItemResponse(ItemBase):  # Response-specific
    id: int
    created_at: datetime
```

### Validators

```python
@field_validator("field")
@classmethod
def validate(cls, v): ...

@model_validator(mode="after")
def validate_model(self): ...
```

---

## Summary

You've learned:

1. **Request models** — Create, Update patterns
2. **Response models** — Filtering output
3. **Validation** — Field constraints, custom validators
4. **Nested models** — Complex structures
5. **Serialization** — Include/exclude, aliases

Next chapter: Dependency Injection — managing dependencies cleanly.
