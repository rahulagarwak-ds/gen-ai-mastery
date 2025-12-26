"""
Copy Utilities Module

Safe copying functions for preventing aliasing bugs.
Critical for any application that modifies data structures.
"""

import copy
from typing import Any, TypeVar

T = TypeVar("T")


def shallow_copy(obj: T) -> T:
    """
    Create a shallow copy of an object.
    
    ONLY the top level is copied. Nested objects are still shared.
    
    Use when:
    - Object has no nested mutable structures
    - You only modify top-level keys
    
    Example:
        >>> original = {"a": 1, "b": [1, 2]}
        >>> copied = shallow_copy(original)
        >>> copied["a"] = 999  # Safe — doesn't affect original
        >>> copied["b"].append(3)  # DANGER — affects original too!
    """
    if isinstance(obj, dict):
        return obj.copy()  # type: ignore
    elif isinstance(obj, list):
        return obj.copy()  # type: ignore
    elif isinstance(obj, set):
        return obj.copy()  # type: ignore
    else:
        return copy.copy(obj)


def deep_copy(obj: T) -> T:
    """
    Create a deep copy of an object.
    
    ALL levels are copied. The new object is completely independent.
    
    Use when:
    - Object has nested dicts/lists
    - You need to modify nested structures safely
    - Caching or storing data that may change
    
    Example:
        >>> original = {"a": 1, "settings": {"debug": True}}
        >>> copied = deep_copy(original)
        >>> copied["settings"]["debug"] = False  # Safe!
        >>> original["settings"]["debug"]  # Still True
    """
    return copy.deepcopy(obj)


def copy_dict_with_override(original: dict, **overrides: Any) -> dict:
    """
    Create a shallow copy of a dict with some keys overridden.
    
    Common pattern for creating variations of config/data.
    
    Example:
        >>> base = {"host": "localhost", "port": 8080, "debug": False}
        >>> dev = copy_dict_with_override(base, debug=True, port=3000)
        >>> dev
        {'host': 'localhost', 'port': 3000, 'debug': True}
    """
    result = original.copy()
    result.update(overrides)
    return result


def merge_dicts(*dicts: dict) -> dict:
    """
    Merge multiple dictionaries into one (shallow).
    
    Later dicts override earlier ones.
    
    Example:
        >>> defaults = {"a": 1, "b": 2}
        >>> custom = {"b": 99, "c": 3}
        >>> merge_dicts(defaults, custom)
        {'a': 1, 'b': 99, 'c': 3}
    """
    result: dict = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge_dicts(base: dict, override: dict) -> dict:
    """
    Recursively merge two dictionaries.
    
    Nested dicts are merged, not replaced.
    
    Example:
        >>> base = {"db": {"host": "localhost", "port": 5432}}
        >>> override = {"db": {"port": 5433}, "cache": {"enabled": True}}
        >>> deep_merge_dicts(base, override)
        {'db': {'host': 'localhost', 'port': 5433}, 'cache': {'enabled': True}}
    """
    result = deep_copy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = deep_copy(value)
    
    return result


def freeze_dict(d: dict) -> tuple:
    """
    Convert a dict to a hashable frozen form.
    
    Useful when you need to use a dict as a dict key or set member.
    
    Example:
        >>> config = {"a": 1, "b": 2}
        >>> frozen = freeze_dict(config)
        >>> {frozen: "some_value"}  # Now usable as dict key
    """
    return tuple(sorted(d.items()))


# === Tests ===
if __name__ == "__main__":
    # Shallow copy test
    original = {"a": 1, "nested": [1, 2]}
    copied = shallow_copy(original)
    copied["a"] = 999
    assert original["a"] == 1, "Shallow copy failed for top-level"
    
    # Deep copy test
    original = {"settings": {"debug": True}}
    copied = deep_copy(original)
    copied["settings"]["debug"] = False
    assert original["settings"]["debug"] is True, "Deep copy failed"
    
    # Override test
    base = {"host": "localhost", "port": 8080}
    result = copy_dict_with_override(base, port=3000)
    assert result["port"] == 3000
    assert base["port"] == 8080  # Original unchanged
    
    # Merge test
    result = merge_dicts({"a": 1}, {"b": 2}, {"a": 99})
    assert result == {"a": 99, "b": 2}
    
    # Deep merge test
    base = {"db": {"host": "localhost", "port": 5432}}
    override = {"db": {"port": 5433}}
    result = deep_merge_dicts(base, override)
    assert result == {"db": {"host": "localhost", "port": 5433}}
    
    # Freeze test
    frozen = freeze_dict({"a": 1, "b": 2})
    assert isinstance(frozen, tuple)
    
    print("✅ All tests passed!")
