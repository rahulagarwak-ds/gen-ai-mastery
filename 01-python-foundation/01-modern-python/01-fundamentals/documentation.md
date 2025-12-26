# Chapter 1: Python Fundamentals

> _"The difference between a script and a production system is the difference between a house of cards and a skyscraper. Both are structures, but only one survives the wind."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- How Python handles data at the memory level
- The complete type system (primitives → composites → special types)
- Operators beyond the basics (identity, membership, bitwise)
- Why `is` vs `==` has broken more production systems than any other bug
- The engineering mindset: writing code that anticipates failure

---

## Prerequisites

- Python 3.10+ installed
- A code editor (VS Code recommended)
- Terminal/command line access

---

## 1. Variables: More Than Just Names

### The Mental Model

In languages like C, a variable is a **box** that holds a value. Change the value, the box stays.

Python is different. A variable is a **sticky note** attached to an object. The object exists independently in memory. Multiple sticky notes can point to the same object.

```python
# Two sticky notes, same object
a = [1, 2, 3]
b = a  # b is NOT a copy. It's the same list.

b.append(4)
print(a)  # [1, 2, 3, 4] — a is also modified!
```

This is called **aliasing**, and it's the source of countless bugs.

### How Python Actually Works

When you write `x = 42`:

1. Python creates an integer object `42` somewhere in memory
2. Python creates a name `x` in the current namespace
3. Python binds (points) `x` to the `42` object

```python
x = 42
y = 42

# Are they the same object?
print(x is y)  # True! (for small integers, Python reuses objects)

x = 1000
y = 1000
print(x is y)  # Could be True or False! (implementation detail)
```

### ⚠️ Common Mistake: Assuming Assignment Creates Copies

```python
# WRONG mental model
original = {"name": "Alice"}
backup = original  # This is NOT a backup!
backup["name"] = "Bob"
print(original)  # {"name": "Bob"} — original is also changed!

# CORRECT approach
import copy
original = {"name": "Alice"}
backup = copy.deepcopy(original)  # True independent copy
backup["name"] = "Bob"
print(original)  # {"name": "Alice"} — original is safe
```

### ✅ Best Practice: Know When You Need Copies

| Scenario                              | Do You Need a Copy?                 |
| ------------------------------------- | ----------------------------------- |
| Passing to a function that reads only | No                                  |
| Modifying data in a function          | Yes (unless intentionally mutating) |
| Storing in a cache                    | Yes (isolate from future changes)   |
| Returning from a function             | Depends on ownership semantics      |

---

## 2. The Type System: A Complete Map

Python's types form a hierarchy. Master this map, and you'll never be confused about what operations are valid.

### 2.1 Numeric Types

| Type      | Example                  | Range      | Use Case                |
| --------- | ------------------------ | ---------- | ----------------------- |
| `int`     | `42`, `-7`, `10_000_000` | Unlimited  | Counting, IDs           |
| `float`   | `3.14`, `2.5e10`         | ±1.8×10³⁰⁸ | Decimals (with caution) |
| `complex` | `3+4j`                   | N/A        | Scientific computing    |
| `bool`    | `True`, `False`          | 0 or 1     | Logic, flags            |

```python
# Integers can be arbitrarily large
big = 10 ** 100  # No overflow, unlike C/Java
print(type(big))  # <class 'int'>

# Floats have precision limits
print(0.1 + 0.2)  # 0.30000000000000004 — NOT 0.3!
```

#### ⚠️ Common Mistake: Float Comparison

```python
# WRONG — will often fail
if 0.1 + 0.2 == 0.3:
    print("Equal")  # Never prints!

# CORRECT — use tolerance
import math
if math.isclose(0.1 + 0.2, 0.3):
    print("Equal")  # Prints correctly
```

#### 🧠 Engineering Thinking: When to Use Decimal

For **money**, **billing**, or anything where cents matter:

```python
from decimal import Decimal

# Float disaster
price = 0.1 + 0.1 + 0.1
print(price)  # 0.30000000000000004

# Decimal precision
price = Decimal("0.1") + Decimal("0.1") + Decimal("0.1")
print(price)  # 0.3 — exact
```

### 2.2 Sequence Types

| Type    | Mutable? | Ordered? | Duplicates? | Example     |
| ------- | -------- | -------- | ----------- | ----------- |
| `list`  | ✅       | ✅       | ✅          | `[1, 2, 3]` |
| `tuple` | ❌       | ✅       | ✅          | `(1, 2, 3)` |
| `str`   | ❌       | ✅       | ✅          | `"hello"`   |
| `range` | ❌       | ✅       | ✅          | `range(10)` |

```python
# List: the workhorse
items = [1, 2, 3]
items.append(4)  # Mutable

# Tuple: immutable, hashable (usable as dict keys)
point = (10, 20)
# point[0] = 5  # TypeError!

# Tuple unpacking — extremely useful
x, y = point
print(f"X: {x}, Y: {y}")
```

### 2.3 Mapping Types

| Type   | Example    | Key Constraint        |
| ------ | ---------- | --------------------- |
| `dict` | `{"a": 1}` | Keys must be hashable |

```python
user = {
    "id": 123,
    "name": "Alice",
    "roles": ["admin", "user"]
}

# Access with .get() to avoid KeyError
email = user.get("email", "not provided")  # Safe default
```

#### ⚠️ Common Mistake: Mutable Default Arguments

```python
# WRONG — the same list is reused across calls!
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))  # ["a"]
print(add_item("b"))  # ["a", "b"] — BUG!

# CORRECT — use None as sentinel
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 2.4 Set Types

| Type        | Mutable? | Example             |
| ----------- | -------- | ------------------- |
| `set`       | ✅       | `{1, 2, 3}`         |
| `frozenset` | ❌       | `frozenset({1, 2})` |

```python
# Sets for membership testing (O(1) vs O(n) for lists)
valid_ids = {101, 102, 103, 104, 105}

if user_id in valid_ids:  # Very fast
    process(user_id)

# Set operations
a = {1, 2, 3}
b = {2, 3, 4}
print(a & b)  # Intersection: {2, 3}
print(a | b)  # Union: {1, 2, 3, 4}
print(a - b)  # Difference: {1}
```

### 2.5 None Type

`None` is Python's null. It's a singleton — there's exactly one `None` object in memory.

```python
# Always use 'is' to check for None
result = some_function()

# WRONG
if result == None:
    pass

# CORRECT
if result is None:
    pass
```

---

## 3. Operators: The Complete Reference

### 3.1 Arithmetic Operators

| Operator | Name           | Example  | Result     |
| -------- | -------------- | -------- | ---------- |
| `+`      | Addition       | `5 + 3`  | `8`        |
| `-`      | Subtraction    | `5 - 3`  | `2`        |
| `*`      | Multiplication | `5 * 3`  | `15`       |
| `/`      | True Division  | `5 / 3`  | `1.666...` |
| `//`     | Floor Division | `5 // 3` | `1`        |
| `%`      | Modulo         | `5 % 3`  | `2`        |
| `**`     | Exponentiation | `5 ** 3` | `125`      |

```python
# Floor division rounds toward negative infinity
print(7 // 3)    # 2
print(-7 // 3)   # -3 (not -2!)

# Divmod gives both at once
quotient, remainder = divmod(17, 5)
print(f"{quotient} remainder {remainder}")  # 3 remainder 2
```

### 3.2 Comparison Operators

| Operator             | Name         | Notes                     |
| -------------------- | ------------ | ------------------------- |
| `==`                 | Equality     | Compares values           |
| `!=`                 | Inequality   | Compares values           |
| `is`                 | Identity     | Compares memory address   |
| `is not`             | Non-identity | Compares memory address   |
| `<`, `>`, `<=`, `>=` | Ordering     | Works on comparable types |

#### 🧠 Engineering Thinking: `is` vs `==`

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True — same values
print(a is b)  # False — different objects in memory
print(a is c)  # True — same object

# Use 'is' ONLY for:
# 1. None checks: if x is None
# 2. Singleton patterns
# 3. Debugging object identity

# Use '==' for everything else
```

### 3.3 Logical Operators

| Operator | Description       |
| -------- | ----------------- |
| `and`    | Short-circuit AND |
| `or`     | Short-circuit OR  |
| `not`    | Negation          |

```python
# Short-circuit evaluation — Python stops early
def expensive_check():
    print("Running expensive check...")
    return True

result = False and expensive_check()  # expensive_check() never runs!
result = True or expensive_check()    # expensive_check() never runs!
```

#### ✅ Best Practice: Use Short-Circuit for Guard Clauses

```python
# Safe dictionary access
if "user" in data and data["user"].get("email"):
    send_email(data["user"]["email"])

# Safe attribute access
if obj is not None and obj.is_valid():
    process(obj)
```

### 3.4 Membership Operators

| Operator | Description            |
| -------- | ---------------------- |
| `in`     | Member of sequence/set |
| `not in` | Not member of          |

```python
# Works on any iterable
"a" in "abc"           # True
1 in [1, 2, 3]         # True
"key" in {"key": "val"}  # True (checks keys)

# Performance tip: use sets for large membership tests
# List: O(n)
# Set: O(1)
```

### 3.5 Bitwise Operators (When You Need Them)

| Operator | Name        | Example         |
| -------- | ----------- | --------------- |
| `&`      | AND         | `5 & 3` = `1`   |
| `\|`     | OR          | `5 \| 3` = `7`  |
| `^`      | XOR         | `5 ^ 3` = `6`   |
| `~`      | NOT         | `~5` = `-6`     |
| `<<`     | Left Shift  | `5 << 1` = `10` |
| `>>`     | Right Shift | `5 >> 1` = `2`  |

Use cases: flags, permissions, low-level protocols, efficient storage.

```python
# Permission flags (common in Unix systems)
READ = 0b100   # 4
WRITE = 0b010  # 2
EXEC = 0b001   # 1

user_perms = READ | WRITE  # 0b110 = 6
has_read = user_perms & READ  # Non-zero = True
```

---

## 4. Type Checking and Introspection

### 4.1 Runtime Type Checking

```python
x = 42
print(type(x))         # <class 'int'>
print(isinstance(x, int))  # True

# isinstance is preferred over type() for checking
# because it respects inheritance
class MyInt(int):
    pass

x = MyInt(42)
print(type(x) == int)     # False
print(isinstance(x, int))  # True
```

### 4.2 The `id()` Function

Every object has a unique identity (memory address).

```python
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(id(a))  # e.g., 140234567890
print(id(b))  # Same as a!
print(id(c))  # Different

print(a is b)  # True (same id)
print(a is c)  # False (different id)
```

---

## 5. The Truth About Truthiness

Python has a concept of "truthy" and "falsy" values.

### Falsy Values (evaluate to `False`):

- `None`
- `False`
- Zero: `0`, `0.0`, `0j`
- Empty sequences: `""`, `[]`, `()`, `{}`
- Empty sets: `set()`
- Objects with `__bool__()` returning `False`
- Objects with `__len__()` returning `0`

### Everything Else is Truthy

```python
# Common pattern: checking for empty collections
if items:  # Truthy if not empty
    process(items)

# Explicit is sometimes clearer
if len(items) > 0:  # Same effect, more explicit
    process(items)
```

#### ⚠️ Common Mistake: Confusing Falsy with None

```python
def get_value():
    return 0  # Valid value, but falsy!

result = get_value()

# WRONG — treats 0 as "no result"
if result:
    print(result)
else:
    print("No result")  # Prints this, even though 0 is valid!

# CORRECT — explicitly check for None
if result is not None:
    print(result)  # Prints 0
```

---

## 6. Variable Naming Conventions

### Python Style Guide (PEP 8)

| Type             | Convention            | Example                     |
| ---------------- | --------------------- | --------------------------- |
| Variables        | `snake_case`          | `user_name`, `total_count`  |
| Constants        | `SCREAMING_SNAKE`     | `MAX_SIZE`, `API_KEY`       |
| Classes          | `PascalCase`          | `UserProfile`, `DataLoader` |
| Private          | `_leading_underscore` | `_internal_cache`           |
| "Really Private" | `__double_leading`    | `__secret` (name mangling)  |
| Dunder/Magic     | `__double_both__`     | `__init__`, `__str__`       |

```python
# Good naming
user_count = 42
MAX_RETRIES = 3
class UserProfile:
    pass

# Bad naming
uc = 42          # Too cryptic
userCount = 42   # Wrong convention (camelCase)
USERPROFILE = 42 # Misleading (looks like constant)
```

### ✅ Best Practice: Self-Documenting Names

```python
# BAD — requires mental parsing
d = {"n": "Alice", "a": 30}
for k, v in d.items():
    print(f"{k}: {v}")

# GOOD — instantly understandable
user_data = {"name": "Alice", "age": 30}
for key, value in user_data.items():
    print(f"{key}: {value}")
```

---

## Quick Reference

### Type Checking

```python
type(x)              # Get type
isinstance(x, int)   # Check type (preferred)
id(x)                # Get memory address
```

### Safe Operations

```python
# Safe division
result = x / y if y != 0 else 0

# Safe dictionary access
value = data.get("key", default_value)

# Safe None check
if x is not None:
    use(x)
```

### Copy Operations

```python
import copy

# Shallow copy (one level deep)
new_list = original.copy()
new_list = list(original)
new_list = original[:]

# Deep copy (all levels)
new_obj = copy.deepcopy(original)
```

---

## Summary

You've learned:

1. **Variables are references**, not boxes — aliasing is real
2. **The complete type hierarchy** — know your tools
3. **`is` vs `==`** — identity vs equality
4. **Short-circuit evaluation** — Python is lazy (in a good way)
5. **Truthiness** — and its dangerous edge cases
6. **When to copy** — protect your data
7. **Naming conventions** — write readable code

Next chapter: Strings and Formatting — the foundation of all output.
