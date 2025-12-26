# Chapter 7: Modern Type System

> _"Types are not about stopping you from making mistakes. They're about catching mistakes before your users do."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Type hints syntax and best practices
- Generic types and TypeVar
- Union, Optional, and the pipe syntax
- TypedDict for structured dictionaries
- Protocols (structural subtyping)
- Annotating functions, classes, and variables
- Using mypy for static analysis

---

## Prerequisites

- Chapters 1-6: All previous content
- Python 3.10+ recommended for modern syntax

---

## 1. Type Hints Basics

### 1.1 Variable Annotations

```python
# Basic types
name: str = "Alice"
age: int = 30
balance: float = 1234.56
is_active: bool = True

# Collections (Python 3.9+)
names: list[str] = ["Alice", "Bob"]
scores: dict[str, int] = {"Alice": 85, "Bob": 92}
coordinates: tuple[float, float] = (10.5, 20.3)
unique_ids: set[int] = {1, 2, 3}
```

### 1.2 Function Annotations

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

def add(a: int, b: int) -> int:
    return a + b

def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# No return value
def log(message: str) -> None:
    print(message)
```

### 1.3 Optional Parameters

```python
# None as possible value
def find_user(user_id: int) -> dict | None:
    # Returns user dict or None if not found
    pass

# Default values
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"
```

---

## 2. Union Types

### 2.1 Modern Syntax (Python 3.10+)

```python
# Value can be either type
user_id: str | int = "abc123"  # or 12345

def parse_input(value: str | int) -> str:
    return str(value)

# Multiple types
def process(data: str | int | float | None) -> str:
    if data is None:
        return "No data"
    return str(data)
```

### 2.2 Optional (Shorthand for X | None)

```python
# These are equivalent
from typing import Optional

# Old style
def find(key: str) -> Optional[dict]:
    pass

# Modern style (preferred)
def find(key: str) -> dict | None:
    pass
```

---

## 3. Generic Types

### 3.1 Built-in Generics

```python
# List of specific type
numbers: list[int] = [1, 2, 3]
users: list[dict[str, str]] = [{"name": "Alice"}]

# Dict with key/value types
cache: dict[str, list[int]] = {
    "scores": [85, 90, 95],
    "ages": [25, 30, 35],
}

# Nested generics
data: dict[str, list[tuple[int, str]]] = {
    "items": [(1, "a"), (2, "b")]
}
```

### 3.2 TypeVar — Creating Generic Functions

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    """Return first item, preserving type."""
    return items[0]

# Type checker knows these return types:
first([1, 2, 3])        # int
first(["a", "b", "c"])  # str
first([{"x": 1}])       # dict[str, int]
```

### 3.3 TypeVar with Bounds

```python
from typing import TypeVar

# T must be a number type
Number = TypeVar("Number", int, float)

def add(a: Number, b: Number) -> Number:
    return a + b

add(1, 2)       # OK: int
add(1.5, 2.5)   # OK: float
add("a", "b")   # Error: str not allowed
```

---

## 4. TypedDict

Structured dictionaries with defined keys.

```python
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    email: str

# Usage
user: User = {
    "id": 1,
    "name": "Alice",
    "email": "alice@example.com"
}

# Type checker catches errors:
user["naem"] = "Bob"  # Error: 'naem' not a key
user["id"] = "abc"    # Error: expected int
```

### Optional Keys

```python
from typing import TypedDict, NotRequired

class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]  # Optional key

# Valid:
cfg1: Config = {"host": "localhost", "port": 8080}
cfg2: Config = {"host": "localhost", "port": 8080, "debug": True}
```

---

## 5. Protocols (Structural Subtyping)

Duck typing with type safety.

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(item: Drawable) -> None:
    item.draw()

# Both work — they have draw() method
render(Circle())  # OK
render(Square())  # OK
```

### Protocol with Properties

```python
from typing import Protocol

class HasName(Protocol):
    @property
    def name(self) -> str:
        ...

class User:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

def greet(thing: HasName) -> str:
    return f"Hello, {thing.name}"

greet(User("Alice"))  # OK
```

---

## 6. Callable Types

Annotating functions as values.

```python
from typing import Callable

# Function that takes two ints and returns int
Operation = Callable[[int, int], int]

def apply(op: Operation, a: int, b: int) -> int:
    return op(a, b)

def add(x: int, y: int) -> int:
    return x + y

apply(add, 3, 5)  # 8
```

---

## 7. Type Aliases

Create readable names for complex types.

```python
# Type alias
UserId = str | int
UserList = list[dict[str, str | int]]

def get_user(user_id: UserId) -> dict | None:
    pass

def process_users(users: UserList) -> None:
    pass

# Python 3.12+ explicit alias
type UserId = str | int
type UserList = list[dict[str, str | int]]
```

---

## 8. Literal Types

Restrict to specific values.

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    print(f"Mode: {mode}")

set_mode("read")    # OK
set_mode("delete")  # Error: not a valid literal

# Useful for status fields
Status = Literal["pending", "active", "completed", "failed"]

def update_status(task_id: int, status: Status) -> None:
    pass
```

---

## 9. Using mypy

### Installation

```bash
pip install mypy
```

### Running

```bash
mypy your_script.py
mypy src/ --strict
```

### Common Configurations (mypy.ini)

```ini
[mypy]
python_version = 3.10
strict = true
ignore_missing_imports = true
```

### Handling External Libraries

```python
# Ignore specific line
result = untyped_function()  # type: ignore

# Type stub packages
pip install types-requests
pip install pandas-stubs
```

---

## ✅ Best Practices

### Do:

```python
# Use modern syntax (3.10+)
def process(data: str | None) -> dict[str, int]:
    pass

# Use TypedDict for structured dicts
class Config(TypedDict):
    host: str
    port: int

# Use Protocols for duck typing
class Serializable(Protocol):
    def to_json(self) -> str: ...
```

### Don't:

```python
# Avoid 'Any' unless necessary
from typing import Any
def process(data: Any) -> Any:  # Defeats the purpose!
    pass

# Avoid overly complex nested types
def func(x: dict[str, list[tuple[int, dict[str, list[str]]]]]):
    pass  # Create type aliases instead
```

---

## Quick Reference

### Common Types

```python
int, str, float, bool, None
list[T], dict[K, V], tuple[T, ...], set[T]
T | None  # Optional
```

### Typing Module

```python
from typing import (
    TypeVar, TypedDict, Protocol,
    Callable, Literal, Final,
    NotRequired, Required
)
```

### Running mypy

```bash
mypy script.py
mypy src/ --strict
```

---

## Summary

You've learned:

1. **Basic annotations** — variables and functions
2. **Union types** — `X | Y` and `X | None`
3. **Generics** — TypeVar for type-preserving functions
4. **TypedDict** — structured dictionaries
5. **Protocols** — duck typing with types
6. **Callable** — typing function parameters
7. **mypy** — static type checking

Next chapter: Functional Programming & Decorators — closures, higher-order functions, and metaprogramming.
