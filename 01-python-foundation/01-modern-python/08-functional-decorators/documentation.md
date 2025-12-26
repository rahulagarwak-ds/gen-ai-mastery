# Chapter 8: Functional Programming & Decorators

> _"Decorators are not magic. They're just functions that return functions. Once you see that, you can build anything."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- First-class functions and closures
- Higher-order functions (map, filter, reduce)
- Lambda functions and their proper use
- Decorator fundamentals and patterns
- functools utilities
- Creating production-ready decorators

---

## Prerequisites

- Chapters 1-7: All previous content, especially Functions & Scope

---

## 1. First-Class Functions

Functions are objects — they can be assigned, passed, and returned.

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Assign to variable
say_hello = greet
print(say_hello("Alice"))  # "Hello, Alice!"

# Store in data structure
operations = [greet, str.upper, str.lower]

# Pass as argument
def apply_to_name(name: str, func):
    return func(name)

apply_to_name("alice", str.upper)  # "ALICE"
```

---

## 2. Closures

A function that "remembers" variables from its enclosing scope.

```python
def make_multiplier(factor: int):
    """Create a function that multiplies by factor."""
    def multiply(x: int) -> int:
        return x * factor  # 'factor' is captured
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15

# factor is "closed over" — it persists even after make_multiplier returns
```

### Practical Use: Counter

```python
def make_counter(start: int = 0):
    count = start

    def counter():
        nonlocal count
        count += 1
        return count

    return counter

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

---

## 3. Higher-Order Functions

Functions that take or return functions.

### 3.1 map() — Transform Each Element

```python
numbers = [1, 2, 3, 4, 5]

# Square each number
squared = list(map(lambda x: x ** 2, numbers))
# [1, 4, 9, 16, 25]

# Often, comprehension is clearer
squared = [x ** 2 for x in numbers]
```

### 3.2 filter() — Select Elements

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Get even numbers
evens = list(filter(lambda x: x % 2 == 0, numbers))
# [2, 4, 6, 8, 10]

# Comprehension alternative
evens = [x for x in numbers if x % 2 == 0]
```

### 3.3 reduce() — Combine Elements

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Sum all (demonstration — use sum() for this)
total = reduce(lambda acc, x: acc + x, numbers)
# 15

# Find maximum (demonstration — use max() for this)
maximum = reduce(lambda a, b: a if a > b else b, numbers)
# 5

# Practical: flatten nested lists
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda acc, lst: acc + lst, nested, [])
# [1, 2, 3, 4, 5, 6]
```

---

## 4. Lambda Functions

Anonymous single-expression functions.

```python
# Basic lambda
add = lambda x, y: x + y
add(3, 5)  # 8

# Common use: sorting key
users = [
    {"name": "Bob", "age": 30},
    {"name": "Alice", "age": 25},
]
sorted(users, key=lambda u: u["age"])

# Common use: quick transformations
list(map(lambda x: x.upper(), ["a", "b", "c"]))
```

### ✅ Best Practice: Keep Lambdas Simple

```python
# GOOD — simple and readable
key_func = lambda x: x["score"]

# BAD — too complex
process = lambda x: x.strip().lower().replace(" ", "_") if x else ""

# BETTER — use regular function
def process(x):
    if not x:
        return ""
    return x.strip().lower().replace(" ", "_")
```

---

## 5. Decorators Fundamentals

A decorator is a function that wraps another function.

### 5.1 Basic Decorator

```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Before function
# Hello!
# After function
```

### 5.2 Decorator with Arguments (Wrapped Function)

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Done")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

add(3, 5)
# Calling add
# Done
# Returns: 8
```

### 5.3 Preserving Metadata with functools.wraps

```python
import functools

def my_decorator(func):
    @functools.wraps(func)  # CRITICAL!
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name: str) -> str:
    """Greet a user."""
    return f"Hello, {name}!"

# Without @wraps:
# greet.__name__ = "wrapper"
# greet.__doc__ = None

# With @wraps:
print(greet.__name__)  # "greet"
print(greet.__doc__)   # "Greet a user."
```

---

## 6. Decorator Patterns

### 6.1 Timing Decorator

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "Done"

slow_function()  # "slow_function took 1.0012s"
```

### 6.2 Retry Decorator

```python
import functools
import time

def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unreliable_api_call():
    # Might fail sometimes
    pass
```

### 6.3 Logging Decorator

```python
import functools
import logging

def log_calls(logger: logging.Logger):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {e}")
                raise
        return wrapper
    return decorator
```

### 6.4 Cache/Memoize (Built-in)

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)  # Instant! Results are cached
```

### 6.5 Validation Decorator

```python
import functools

def validate_types(**expected_types):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check kwargs
            for param, expected in expected_types.items():
                if param in kwargs:
                    value = kwargs[param]
                    if not isinstance(value, expected):
                        raise TypeError(f"{param} must be {expected.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def create_user(name, age):
    return {"name": name, "age": age}

create_user(name="Alice", age=30)   # OK
create_user(name="Alice", age="30") # TypeError!
```

---

## 7. Class Decorators

### 7.1 Decorating a Class

```python
def add_repr(cls):
    """Add a default __repr__ to a class."""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"
    cls.__repr__ = __repr__
    return cls

@add_repr
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

print(User("Alice", 30))
# User(name='Alice', age=30)
```

### 7.2 Using a Class as a Decorator

```python
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call {self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    return f"Hello, {name}!"

greet("Alice")  # Call 1 to greet
greet("Bob")    # Call 2 to greet
print(greet.count)  # 2
```

---

## 8. functools Utilities

### 8.1 partial — Pre-fill Arguments

```python
from functools import partial

def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

square(5)  # 25
cube(5)    # 125
```

### 8.2 lru_cache — Memoization

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def expensive_computation(x, y):
    # Simulating expensive work
    return x ** y

# First call: computed
expensive_computation(2, 10)

# Second call: retrieved from cache
expensive_computation(2, 10)

# Check cache stats
expensive_computation.cache_info()
```

### 8.3 cached_property (Python 3.8+)

```python
from functools import cached_property

class DataLoader:
    @cached_property
    def data(self):
        print("Loading data...")
        return [1, 2, 3, 4, 5]

loader = DataLoader()
loader.data  # "Loading data..." then [1, 2, 3, 4, 5]
loader.data  # [1, 2, 3, 4, 5] — no loading, cached
```

---

## Quick Reference

### Higher-Order Functions

```python
map(func, iterable)      # Transform each
filter(func, iterable)   # Select matching
reduce(func, iterable)   # Combine all
```

### Decorator Template

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Before
        result = func(*args, **kwargs)
        # After
        return result
    return wrapper
```

### Decorator with Arguments Template

```python
def decorator_with_args(arg1, arg2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use arg1, arg2
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## Summary

You've learned:

1. **First-class functions** — functions as values
2. **Closures** — functions with captured state
3. **Higher-order functions** — map, filter, reduce
4. **Lambda functions** — anonymous expressions
5. **Decorators** — wrapping and enhancing functions
6. **Decorator patterns** — timing, retry, cache, validation
7. **functools** — partial, lru_cache, cached_property

Next chapter: Error Handling — exceptions, context managers, and defensive programming.
