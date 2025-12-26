# Chapter 11: Dataclasses & Pydantic

> _"Dictionaries are chaos. Structured data is sanity. Validated data is safety."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Python's built-in `@dataclass`
- Field options and customization
- Pydantic v2 basics
- Validation and coercion
- Nested models
- Serialization (JSON)
- When to use which

---

## Prerequisites

- Chapters 1-10: All previous content, especially OOP and Type System

---

## 1. The Problem with Dictionaries

```python
# Unstructured chaos
user = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

# Problems:
user["nmae"]              # KeyError — typo
user["age"] = "thirty"    # No type checking
user.get("role")          # None — missing key?
```

We need structured, typed, validated data.

---

## 2. Dataclasses

### 2.1 Basic Dataclass

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str

# Auto-generated __init__, __repr__, __eq__
alice = User(name="Alice", age=30, email="alice@example.com")
print(alice)
# User(name='Alice', age=30, email='alice@example.com')

# Type hints are metadata only — no runtime validation!
bob = User(name="Bob", age="thirty", email="bob@example.com")
# Works! (but age is a string, not int)
```

### 2.2 Default Values

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int
    email: str = ""  # Simple default
    roles: list[str] = field(default_factory=list)  # Mutable default

alice = User(name="Alice", age=30)
print(alice.roles)  # []
```

### 2.3 Frozen Dataclasses (Immutable)

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(10, 20)
p.x = 5  # FrozenInstanceError!

# Hashable — can be dict key or set member
points = {Point(0, 0), Point(1, 1)}
```

### 2.4 Post-Init Processing

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    email: str
    username: str = field(init=False)  # Not in __init__

    def __post_init__(self):
        # Runs after __init__
        self.username = self.email.split("@")[0].lower()

alice = User(name="Alice", email="Alice.Smith@example.com")
print(alice.username)  # "alice.smith"
```

### 2.5 Comparison and Ordering

```python
@dataclass(order=True)
class Product:
    sort_index: int = field(init=False, repr=False)
    name: str
    price: float

    def __post_init__(self):
        self.sort_index = self.price  # Sort by price

products = [
    Product("Laptop", 999),
    Product("Mouse", 29),
    Product("Keyboard", 79),
]

sorted(products)
# [Product(name='Mouse', price=29), Product(name='Keyboard', price=79), ...]
```

---

## 3. Pydantic v2

Pydantic provides runtime validation, coercion, and serialization.

### 3.1 Installation

```bash
pip install pydantic
```

### 3.2 Basic Model

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

# Valid data
alice = User(name="Alice", age=30, email="alice@example.com")

# Coercion — "30" becomes 30
bob = User(name="Bob", age="30", email="bob@example.com")
print(bob.age)  # 30 (int, not str)

# Invalid data — raises ValidationError!
try:
    invalid = User(name="Charlie", age="not a number", email="charlie@example.com")
except Exception as e:
    print(e)
# validation error for User
# age: Input should be a valid integer, unable to parse string as an integer
```

### 3.3 Field Validation

```python
from pydantic import BaseModel, Field, field_validator

class User(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=150)  # 0 <= age <= 150
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()

# Validation enforced
user = User(name="Alice", age=30, email="ALICE@Example.com")
print(user.email)  # "alice@example.com" (lowercased)

# Validation fails
User(name="", age=30, email="alice@example.com")
# ValidationError: name: String should have at least 1 character
```

### 3.4 Optional and Default Values

```python
from pydantic import BaseModel

class Config(BaseModel):
    host: str
    port: int = 8080
    debug: bool = False
    tags: list[str] = []  # Mutable defaults work in Pydantic!

# Minimal
cfg = Config(host="localhost")
print(cfg.port)  # 8080
print(cfg.tags)  # []
```

### 3.5 Nested Models

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    country: str = "USA"

class User(BaseModel):
    name: str
    email: str
    address: Address

# Nested validation
user = User(
    name="Alice",
    email="alice@example.com",
    address={"street": "123 Main St", "city": "NYC"}  # Dict auto-converted
)
print(user.address.city)  # "NYC"
```

### 3.6 Serialization

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

alice = User(name="Alice", age=30, email="alice@example.com")

# To dict
data = alice.model_dump()
# {'name': 'Alice', 'age': 30, 'email': 'alice@example.com'}

# To JSON string
json_str = alice.model_dump_json()
# '{"name":"Alice","age":30,"email":"alice@example.com"}'

# From dict/JSON
user = User.model_validate(data)
user = User.model_validate_json(json_str)
```

### 3.7 Custom Types and Constraints

```python
from pydantic import BaseModel, EmailStr, HttpUrl, conint, confloat

class Config(BaseModel):
    email: EmailStr  # Must be valid email
    website: HttpUrl  # Must be valid URL
    port: conint(ge=1, le=65535)  # Constrained int
    rate: confloat(gt=0, lt=1)  # Constrained float

# Note: EmailStr requires 'pip install email-validator'
```

### 3.8 Computed Fields

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

rect = Rectangle(width=10, height=5)
print(rect.area)  # 50.0
print(rect.model_dump())  # {'width': 10.0, 'height': 5.0, 'area': 50.0}
```

---

## 4. Pydantic for Gen AI

Why Pydantic is critical for LLM applications:

### 4.1 Structured LLM Output

```python
from pydantic import BaseModel

class ExtractedData(BaseModel):
    name: str
    skills: list[str]
    years_experience: int

# LLM returns JSON, Pydantic validates
llm_response = '{"name": "Alice", "skills": ["Python", "ML"], "years_experience": 5}'
data = ExtractedData.model_validate_json(llm_response)
```

### 4.2 API Request/Response Models

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    messages: list[dict[str, str]]
    model: str = "gpt-4"
    temperature: float = 0.7

class ChatResponse(BaseModel):
    content: str
    tokens_used: int
    model: str
```

### 4.3 Configuration Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4"
    temperature: float = 0.7

    class Config:
        env_file = ".env"

settings = Settings()  # Loads from environment variables
```

---

## 5. Dataclass vs Pydantic

| Feature            | dataclass   | Pydantic        |
| ------------------ | ----------- | --------------- |
| Runtime validation | ❌          | ✅              |
| Type coercion      | ❌          | ✅              |
| JSON serialization | ❌ (manual) | ✅              |
| Schema generation  | ❌          | ✅              |
| Performance        | Faster      | Slightly slower |
| Built-in           | ✅          | ❌ (external)   |

**Use dataclass when:**

- Internal data structures
- Performance critical
- No external input

**Use Pydantic when:**

- External data (APIs, files, user input)
- Need validation
- Need serialization

---

## Quick Reference

### Dataclass

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class MyClass:
    required: str
    optional: str = "default"
    mutable: list = field(default_factory=list)
```

### Pydantic

```python
from pydantic import BaseModel, Field, field_validator

class MyModel(BaseModel):
    required: str
    optional: str = "default"
    validated: int = Field(ge=0, le=100)

    @field_validator("required")
    @classmethod
    def check_required(cls, v):
        # Custom validation
        return v

# Serialization
model.model_dump()
model.model_dump_json()
Model.model_validate(data)
```

---

## Summary

You've learned:

1. **Dataclasses** — structured data with auto-generated methods
2. **Frozen dataclasses** — immutable, hashable
3. **Pydantic models** — validation and coercion
4. **Field validation** — constraints and custom validators
5. **Nested models** — complex data structures
6. **Serialization** — dict/JSON conversion
7. **When to use which** — dataclass for internal, Pydantic for external

**🎉 You've completed Modern Python!**

Next: Move to Month 1's Dev Tooling module, or start the CLI Data Processor capstone project.
