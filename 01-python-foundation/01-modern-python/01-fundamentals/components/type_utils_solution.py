"""
Type Utilities Module

Production-ready utilities for type checking and validation.
Use these in larger applications for consistent type handling.
"""

from typing import Any, TypeGuard


def is_none(value: Any) -> TypeGuard[None]:
    """
    Check if value is None.
    
    Always use this or 'is None' — never '== None'.
    
    Example:
        >>> is_none(None)
        True
        >>> is_none(0)
        False
        >>> is_none("")
        False
    """
    return value is None


def is_not_none(value: Any) -> bool:
    """
    Check if value is not None.
    
    Example:
        >>> is_not_none(0)
        True
        >>> is_not_none("")
        True
        >>> is_not_none(None)
        False
    """
    return value is not None


def is_truthy(value: Any) -> bool:
    """
    Check if value is truthy (Python's boolean coercion).
    
    Falsy values: None, False, 0, 0.0, '', [], {}, set()
    
    Example:
        >>> is_truthy([1, 2, 3])
        True
        >>> is_truthy([])
        False
        >>> is_truthy(0)
        False
    """
    return bool(value)


def is_numeric(value: Any) -> TypeGuard[int | float]:
    """
    Check if value is a number (int or float, but NOT bool).
    
    Note: In Python, bool is a subclass of int, so we explicitly exclude it.
    
    Example:
        >>> is_numeric(42)
        True
        >>> is_numeric(3.14)
        True
        >>> is_numeric(True)
        False
        >>> is_numeric("42")
        False
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_string(value: Any) -> TypeGuard[str]:
    """
    Check if value is a string.
    
    Example:
        >>> is_string("hello")
        True
        >>> is_string(42)
        False
    """
    return isinstance(value, str)


def is_collection(value: Any) -> TypeGuard[list | tuple | set | frozenset]:
    """
    Check if value is a collection (list, tuple, set, frozenset).
    
    Note: Does NOT include dict or str (which are iterable but not "collections" in this sense).
    
    Example:
        >>> is_collection([1, 2])
        True
        >>> is_collection((1, 2))
        True
        >>> is_collection({1, 2})
        True
        >>> is_collection({"a": 1})
        False
        >>> is_collection("hello")
        False
    """
    return isinstance(value, (list, tuple, set, frozenset))


def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary.
    
    Wrapper around dict.get() for consistency and clarity.
    
    Example:
        >>> safe_get({"name": "Alice"}, "name")
        'Alice'
        >>> safe_get({"name": "Alice"}, "email", "not found")
        'not found'
    """
    return data.get(key, default)


def safe_nested_get(data: dict, *keys: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary.
    
    Navigates through nested dicts without raising KeyError.
    
    Example:
        >>> data = {"user": {"profile": {"name": "Alice"}}}
        >>> safe_nested_get(data, "user", "profile", "name")
        'Alice'
        >>> safe_nested_get(data, "user", "settings", "theme", default="dark")
        'dark'
    """
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current


# === Tests (run this file directly to test) ===
if __name__ == "__main__":
    # Type checks
    assert is_none(None) is True
    assert is_none(0) is False
    assert is_not_none(0) is True
    
    assert is_truthy([1]) is True
    assert is_truthy([]) is False
    
    assert is_numeric(42) is True
    assert is_numeric(3.14) is True
    assert is_numeric(True) is False  # bool excluded!
    
    assert is_string("hello") is True
    assert is_string(42) is False
    
    assert is_collection([1, 2]) is True
    assert is_collection("abc") is False
    
    # Safe access
    assert safe_get({"a": 1}, "a") == 1
    assert safe_get({"a": 1}, "b", "default") == "default"
    
    nested = {"level1": {"level2": {"value": 42}}}
    assert safe_nested_get(nested, "level1", "level2", "value") == 42
    assert safe_nested_get(nested, "level1", "missing", default="N/A") == "N/A"
    
    print("✅ All tests passed!")
