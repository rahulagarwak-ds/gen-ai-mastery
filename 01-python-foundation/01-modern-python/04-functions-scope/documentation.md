# Chapter 4: Functions & Scope

> _"Functions are the building blocks of reusable code. Master their nuances, and you master program structure."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Function definition and calling
- Parameters: positional, keyword, default, \*args, \*\*kwargs
- Return values and multiple returns
- Scope: local, global, nonlocal, and the LEGB rule
- Docstrings and type hints
- Lambda functions
- Common function patterns and anti-patterns

---

## Prerequisites

- Chapter 1-3: Fundamentals, Strings, Control Flow

---

## 1. Function Basics

### 1.1 Defining and Calling Functions

```python
# Definition
def greet(name):
    """Greet a user by name."""
    return f"Hello, {name}!"

# Calling
message = greet("Alice")
print(message)  # Hello, Alice!
```

### 1.2 Parameters vs Arguments

- **Parameters**: Variables in function definition
- **Arguments**: Values passed when calling

```python
def add(a, b):  # a, b are parameters
    return a + b

result = add(3, 5)  # 3, 5 are arguments
```

### 1.3 Return Values

```python
# Single return
def square(x):
    return x ** 2

# Multiple returns (tuple unpacking)
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, avg = get_stats([1, 2, 3, 4, 5])

# No explicit return → returns None
def log(message):
    print(message)

result = log("Hello")  # Prints "Hello"
print(result)  # None
```

---

## 2. Parameter Types

### 2.1 Positional Parameters

Arguments matched by position.

```python
def power(base, exponent):
    return base ** exponent

power(2, 3)  # 8 (base=2, exponent=3)
power(3, 2)  # 9 (base=3, exponent=2)
```

### 2.2 Keyword Parameters

Arguments passed by name.

```python
power(base=2, exponent=3)  # 8
power(exponent=3, base=2)  # 8 (order doesn't matter)

# Mix positional and keyword
power(2, exponent=3)  # 8 (positional first!)
```

#### ⚠️ Common Mistake: Positional After Keyword

```python
# WRONG — positional after keyword
power(base=2, 3)  # SyntaxError!

# RIGHT — positional first
power(2, exponent=3)
```

### 2.3 Default Parameters

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Alice")              # "Hello, Alice!"
greet("Alice", "Hi")        # "Hi, Alice!"
greet("Alice", greeting="Hey")  # "Hey, Alice!"
```

#### ⚠️ CRITICAL: Mutable Default Trap

```python
# WRONG — shared mutable default!
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item("a"))  # ["a"]
print(add_item("b"))  # ["a", "b"] — BUG!

# CORRECT — use None sentinel
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item("a"))  # ["a"]
print(add_item("b"))  # ["b"] — correct!
```

### 2.4 \*args — Variable Positional Arguments

Collect extra positional arguments as a tuple.

```python
def sum_all(*numbers):
    return sum(numbers)

sum_all(1, 2, 3)        # 6
sum_all(1, 2, 3, 4, 5)  # 15
sum_all()               # 0

# Combine with regular parameters
def greet(greeting, *names):
    for name in names:
        print(f"{greeting}, {name}!")

greet("Hello", "Alice", "Bob", "Charlie")
# Hello, Alice!
# Hello, Bob!
# Hello, Charlie!
```

### 2.5 \*\*kwargs — Variable Keyword Arguments

Collect extra keyword arguments as a dict.

```python
def create_user(**details):
    return details

create_user(name="Alice", age=30, city="NYC")
# {'name': 'Alice', 'age': 30, 'city': 'NYC'}

# Combine with regular parameters
def log(message, **metadata):
    print(f"[LOG] {message}")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

log("User login", user="alice", ip="192.168.1.1")
```

### 2.6 The Full Parameter Order

```python
def func(pos1, pos2, *args, kw1, kw2="default", **kwargs):
    pass

# Order: positional → *args → keyword-only → **kwargs

func(1, 2, 3, 4, kw1="required", extra="value")
# pos1=1, pos2=2, args=(3, 4), kw1="required", kw2="default", kwargs={'extra': 'value'}
```

### 2.7 Keyword-Only Arguments

Force arguments to be passed by name (after \*).

```python
def fetch(url, *, timeout=30, verify=True):
    pass

fetch("http://example.com", timeout=10)  # OK
fetch("http://example.com", 10)  # TypeError! timeout is keyword-only
```

### 2.8 Positional-Only Arguments (Python 3.8+)

Force arguments to be passed by position (before /).

```python
def divide(a, b, /):
    return a / b

divide(10, 2)       # OK
divide(a=10, b=2)   # TypeError! a and b are positional-only
```

---

## 3. Scope: Where Variables Live

### 3.1 The LEGB Rule

Python looks up names in this order:

1. **L**ocal — Inside current function
2. **E**nclosing — Inside enclosing functions
3. **G**lobal — Module level
4. **B**uilt-in — Python's built-in names

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)  # "local"

    inner()
    print(x)  # "enclosing"

outer()
print(x)  # "global"
```

### 3.2 The `global` Keyword

Modify global variables from inside a function.

```python
counter = 0

def increment():
    global counter
    counter += 1

increment()
increment()
print(counter)  # 2
```

#### ⚠️ Common Mistake: Forgetting global

```python
counter = 0

def increment():
    counter += 1  # UnboundLocalError!
    # Python sees assignment, assumes local, but local doesn't exist yet

increment()
```

### 3.3 The `nonlocal` Keyword

Modify enclosing (not global) variables.

```python
def counter():
    count = 0

    def increment():
        nonlocal count
        count += 1
        return count

    return increment

inc = counter()
print(inc())  # 1
print(inc())  # 2
print(inc())  # 3
```

### 3.4 Shadowing

Local variables can "shadow" outer ones.

```python
data = [1, 2, 3]

def process():
    data = [4, 5, 6]  # Shadows global data
    print(data)  # [4, 5, 6]

process()
print(data)  # [1, 2, 3] — global unchanged
```

#### ✅ Best Practice: Avoid Shadowing Built-ins

```python
# BAD — shadows built-in
list = [1, 2, 3]  # Now list() is broken!
id = 42           # Now id() is broken!

# GOOD — use descriptive names
user_list = [1, 2, 3]
user_id = 42
```

---

## 4. Docstrings and Type Hints

### 4.1 Docstrings

```python
def calculate_total(prices, tax_rate):
    """
    Calculate total price including tax.

    Args:
        prices: List of item prices.
        tax_rate: Tax rate as decimal (0.1 = 10%).

    Returns:
        Total price including tax.

    Raises:
        ValueError: If tax_rate is negative.

    Example:
        >>> calculate_total([10, 20, 30], 0.1)
        66.0
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")
    subtotal = sum(prices)
    return subtotal * (1 + tax_rate)
```

### 4.2 Type Hints (Python 3.9+)

```python
def calculate_total(
    prices: list[float],
    tax_rate: float = 0.0
) -> float:
    """Calculate total with tax."""
    return sum(prices) * (1 + tax_rate)

# Complex types
from typing import Optional, Union

def find_user(user_id: int) -> Optional[dict]:
    """Return user dict or None if not found."""
    pass

def process(value: Union[str, int]) -> str:
    """Accept string or int, return string."""
    return str(value)

# Python 3.10+ syntax
def process(value: str | int) -> str:
    return str(value)
```

---

## 5. Lambda Functions

Anonymous single-expression functions.

```python
# Regular function
def square(x):
    return x ** 2

# Lambda equivalent
square = lambda x: x ** 2

# Common use: sorting key
users = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
sorted_users = sorted(users, key=lambda u: u["age"])

# Common use: filtering
numbers = [1, 2, 3, 4, 5, 6]
evens = list(filter(lambda x: x % 2 == 0, numbers))

# Common use: mapping
doubled = list(map(lambda x: x * 2, numbers))
```

#### ✅ Best Practice: Keep Lambdas Simple

```python
# GOOD — simple and clear
key_func = lambda x: x["name"].lower()

# BAD — too complex, use regular function
process = lambda x: x.strip().lower().replace(" ", "_") if x else "default"

# BETTER
def process(x):
    if not x:
        return "default"
    return x.strip().lower().replace(" ", "_")
```

---

## 6. First-Class Functions

Functions are objects — they can be passed, returned, and stored.

### 6.1 Functions as Arguments

```python
def apply_operation(numbers, operation):
    return [operation(n) for n in numbers]

def double(x):
    return x * 2

def square(x):
    return x ** 2

nums = [1, 2, 3, 4]
print(apply_operation(nums, double))  # [2, 4, 6, 8]
print(apply_operation(nums, square))  # [1, 4, 9, 16]
```

### 6.2 Functions Returning Functions

```python
def create_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply

double = create_multiplier(2)
triple = create_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

---

## 7. Common Patterns

### 7.1 Guard Clauses (Early Return)

```python
# BAD — deep nesting
def process_user(user):
    if user is not None:
        if user.is_active:
            if user.has_permission:
                do_work(user)

# GOOD — flat with early returns
def process_user(user):
    if user is None:
        return
    if not user.is_active:
        return
    if not user.has_permission:
        return

    do_work(user)
```

### 7.2 Default Factory Pattern

```python
def get_or_create(data, key, factory=dict):
    """Get value or create with factory function."""
    if key not in data:
        data[key] = factory()
    return data[key]

cache = {}
user_data = get_or_create(cache, "user_123", dict)
user_data["name"] = "Alice"
```

### 7.3 Configuration With \*\*kwargs

```python
def create_connection(host, port, **options):
    """Create connection with optional settings."""
    config = {
        "timeout": 30,
        "retries": 3,
        "verify": True,
        **options  # Override defaults
    }
    return connect(host, port, config)

conn = create_connection("localhost", 5432, timeout=60, retries=5)
```

---

## 8. Anti-Patterns

### ❌ Modifying Arguments

```python
# BAD — surprises the caller!
def process(items):
    items.clear()  # Modifies original list!
    # ... do work

# GOOD — work on a copy
def process(items):
    items = items.copy()  # or list(items)
    items.clear()
    # ... do work
```

### ❌ Too Many Parameters

```python
# BAD — hard to remember order
def create_user(name, email, age, city, country, role, active, verified):
    pass

# GOOD — use a data class or dict
def create_user(user_data: dict):
    pass

# OR use keyword-only
def create_user(*, name, email, age, **optional):
    pass
```

### ❌ God Functions

```python
# BAD — does too many things
def process_order(order):
    validate_order(order)
    calculate_totals(order)
    apply_discounts(order)
    create_invoice(order)
    send_email(order)
    update_inventory(order)
    # ... 500 more lines

# GOOD — compose smaller functions
def process_order(order):
    order = validate(order)
    order = calculate(order)
    order = discount(order)
    notify(order)
    fulfill(order)
```

---

## Quick Reference

### Parameter Types

```python
def func(pos, /, pos_or_kw, *, kw_only, **kwargs):
    pass
```

### Scope Keywords

```python
global x    # Use global variable
nonlocal x  # Use enclosing variable
```

### Common Built-ins

```python
len, max, min, sum, sorted, map, filter, zip, enumerate
```

### Type Hints

```python
def func(x: int, y: str = "default") -> bool:
    pass
```

---

## Summary

You've learned:

1. **Parameters**: positional, keyword, default, \*args, \*\*kwargs
2. **Mutable default trap** — always use None sentinel
3. **LEGB scope** — Local → Enclosing → Global → Built-in
4. **global/nonlocal** — modifying outer variables
5. **Docstrings + Type hints** — document your contracts
6. **Lambdas** — simple anonymous functions
7. **First-class functions** — pass and return functions

Next chapter: Data Structures Deep Dive — lists, dicts, sets in depth.
