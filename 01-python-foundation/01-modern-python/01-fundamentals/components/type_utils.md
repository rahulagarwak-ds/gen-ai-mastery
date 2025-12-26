# Mini Project: Type Utilities Module

## 🎯 Objective

Build a production-ready type checking utilities module that provides safe type operations commonly needed in Python applications.

---

## 📋 Requirements

### 1. Type Guard Functions

Create functions that safely check types with proper TypeGuard annotations:

```python
def is_string(value: Any) -> TypeGuard[str]:
    """Check if value is a string."""
    pass

def is_int(value: Any) -> TypeGuard[int]:
    """Check if value is an integer (not bool)."""
    pass

def is_list_of(value: Any, item_type: type) -> bool:
    """Check if value is a list of specific type."""
    pass
```

### 2. Safe Dictionary Access

Create utilities for safely accessing nested dictionary values:

```python
def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """Get value from dict with default."""
    pass

def nested_get(data: dict, path: str, default: Any = None, sep: str = ".") -> Any:
    """
    Get nested value using dot notation.

    Example:
        data = {"user": {"profile": {"name": "Alice"}}}
        nested_get(data, "user.profile.name")  # "Alice"
        nested_get(data, "user.missing.key", "default")  # "default"
    """
    pass
```

### 3. Type Coercion

Create safe type conversion functions:

```python
def to_int(value: Any, default: int = 0) -> int:
    """Safely convert to int, return default on failure."""
    pass

def to_float(value: Any, default: float = 0.0) -> float:
    """Safely convert to float, return default on failure."""
    pass

def to_bool(value: Any) -> bool:
    """
    Convert to bool handling string values.

    "true", "1", "yes" -> True
    "false", "0", "no" -> False
    """
    pass
```

---

## ✅ Test Cases

Your implementation should pass these tests:

```python
# TypeGuard tests
assert is_string("hello") == True
assert is_string(123) == False
assert is_int(42) == True
assert is_int(True) == False  # bool is not int!

# Safe access tests
data = {"a": {"b": {"c": 1}}}
assert nested_get(data, "a.b.c") == 1
assert nested_get(data, "a.x.y", "default") == "default"

# Coercion tests
assert to_int("42") == 42
assert to_int("invalid", -1) == -1
assert to_bool("yes") == True
assert to_bool("false") == False
```

---

## 🏆 Bonus Challenges

1. Add `deep_get` that works with both dicts and lists: `deep_get(data, "users.0.name")`
2. Add type hints using `TypeVar` for generic functions
3. Add `is_dict_like` that checks for Mapping protocol

---

## 📁 Deliverable

Create `type_utils.py` with all functions, proper type hints, and docstrings.

**Time estimate:** 30-45 minutes

---

## 💡 Hints (only if stuck)

<details>
<summary>Hint 1: TypeGuard</summary>

```python
from typing import TypeGuard, Any

def is_string(value: Any) -> TypeGuard[str]:
    return isinstance(value, str)
```

</details>

<details>
<summary>Hint 2: Nested Get</summary>

Split the path and traverse step by step, handling KeyError.

</details>
