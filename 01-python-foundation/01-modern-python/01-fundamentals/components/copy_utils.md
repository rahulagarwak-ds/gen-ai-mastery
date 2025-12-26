# Mini Project: Copy Utilities Module

## 🎯 Objective

Build a utilities module for safe copying and merging of Python data structures, handling the common pitfalls of mutable object references.

---

## 📋 Requirements

### 1. Safe Copy Functions

```python
def shallow_copy(obj: Any) -> Any:
    """
    Create a shallow copy of an object.
    Handle: dict, list, set, and fallback for others.
    """
    pass

def deep_copy(obj: Any) -> Any:
    """
    Create a deep copy of an object.
    Use copy.deepcopy but handle edge cases.
    """
    pass
```

### 2. Dictionary Merge Utilities

```python
def merge_dicts(*dicts: dict) -> dict:
    """
    Merge multiple dicts (later values override earlier).

    Example:
        merge_dicts({"a": 1}, {"b": 2}, {"a": 3})
        # {"a": 3, "b": 2}
    """
    pass

def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dicts (recursively merge nested dicts).

    Example:
        base = {"a": {"x": 1, "y": 2}}
        override = {"a": {"y": 3, "z": 4}}
        deep_merge(base, override)
        # {"a": {"x": 1, "y": 3, "z": 4}}
    """
    pass
```

### 3. Safe Override Utilities

```python
def safe_update(target: dict, source: dict, keys: list[str] | None = None) -> dict:
    """
    Update target with source values, optionally only specific keys.
    Returns a NEW dict (doesn't mutate target).

    Example:
        target = {"a": 1, "b": 2, "c": 3}
        source = {"a": 10, "b": 20, "d": 40}
        safe_update(target, source, keys=["a", "b"])
        # {"a": 10, "b": 20, "c": 3}
    """
    pass

def without_keys(d: dict, keys: list[str]) -> dict:
    """
    Return a new dict without the specified keys.

    Example:
        without_keys({"a": 1, "b": 2, "c": 3}, ["a", "c"])
        # {"b": 2}
    """
    pass

def pick_keys(d: dict, keys: list[str]) -> dict:
    """
    Return a new dict with only the specified keys.

    Example:
        pick_keys({"a": 1, "b": 2, "c": 3}, ["a", "c"])
        # {"a": 1, "c": 3}
    """
    pass
```

---

## ✅ Test Cases

```python
# Deep copy test
original = {"users": [{"name": "Alice"}]}
copied = deep_copy(original)
copied["users"][0]["name"] = "Bob"
assert original["users"][0]["name"] == "Alice"  # Original unchanged!

# Merge test
assert merge_dicts({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}

# Deep merge test
base = {"config": {"debug": True, "port": 8080}}
override = {"config": {"port": 9000}}
result = deep_merge(base, override)
assert result == {"config": {"debug": True, "port": 9000}}

# Pick/without tests
d = {"a": 1, "b": 2, "c": 3}
assert pick_keys(d, ["a", "b"]) == {"a": 1, "b": 2}
assert without_keys(d, ["b"]) == {"a": 1, "c": 3}
```

---

## 🏆 Bonus Challenges

1. Add `frozen_dict` that returns an immutable dict-like object
2. Handle circular references in `deep_copy`
3. Add `diff_dicts(a, b)` that returns what changed between two dicts

---

## 📁 Deliverable

Create `copy_utils.py` with all functions, proper type hints, and docstrings.

**Time estimate:** 30-45 minutes

---

## 💡 Hints

<details>
<summary>Hint 1: Deep Merge</summary>

Use recursion. Check if both values are dicts, if so, recursively merge.

</details>

<details>
<summary>Hint 2: Safe Update</summary>

Start with a copy of target, then update only specified keys.

</details>
