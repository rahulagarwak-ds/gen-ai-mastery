# Chapter 3: Control Flow

> _"A program that can't make decisions is just an expensive calculator."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Conditional statements (if/elif/else) and their patterns
- All loop types and when to use each
- Loop control (break, continue, else)
- The new match/case statement (3.10+)
- Common control flow patterns in production code
- Anti-patterns to avoid

---

## Prerequisites

- Chapter 1: Python Fundamentals
- Chapter 2: Strings & Formatting

---

## 1. Conditional Statements

### 1.1 The `if` Statement

```python
age = 25

if age >= 18:
    print("Adult")
```

### 1.2 `if-else`

```python
age = 15

if age >= 18:
    print("Adult")
else:
    print("Minor")
```

### 1.3 `if-elif-else` Chain

```python
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Grade: {grade}")  # Grade: B
```

#### ⚠️ Common Mistake: Order Matters!

```python
score = 95

# WRONG — first match wins, so 95 gets "C" grade
if score >= 70:
    grade = "C"
elif score >= 80:
    grade = "B"  # Never reached for 95!
elif score >= 90:
    grade = "A"  # Never reached!

# CORRECT — most restrictive first
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
```

### 1.4 Ternary Operator (Conditional Expression)

Single-line if-else for simple cases.

```python
age = 20

# Traditional
if age >= 18:
    status = "adult"
else:
    status = "minor"

# Ternary (cleaner for simple cases)
status = "adult" if age >= 18 else "minor"
```

#### ✅ Best Practice: Keep Ternary Simple

```python
# GOOD — simple and readable
result = "even" if x % 2 == 0 else "odd"

# BAD — too complex, use regular if-else
result = "high" if x > 100 else "medium" if x > 50 else "low"
```

### 1.5 Truthy/Falsy in Conditions

Python allows any value in conditions, not just booleans.

```python
# These work because of truthiness
if items:  # Same as: if len(items) > 0
    process(items)

if name:  # Same as: if name != ""
    greet(name)

if result:  # Same as: if result is not None and result != 0
    use(result)
```

#### ⚠️ Common Mistake: Falsy Pitfall

```python
# WRONG — 0 is a valid value but falsy!
count = get_count()  # Returns 0
if count:
    print(f"Count: {count}")  # Never prints when count is 0!

# CORRECT — explicit check
if count is not None:
    print(f"Count: {count}")  # Prints "Count: 0"
```

---

## 2. Loops

### 2.1 The `for` Loop

Iterate over any iterable (list, tuple, string, dict, range, etc.).

```python
# Iterate over list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Iterate over string
for char in "hello":
    print(char)

# Iterate over range
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

# Iterate over dict (keys by default)
data = {"a": 1, "b": 2}
for key in data:
    print(key)

# Iterate over dict items
for key, value in data.items():
    print(f"{key}: {value}")
```

### 2.2 The `range()` Function

```python
range(5)          # 0, 1, 2, 3, 4
range(1, 6)       # 1, 2, 3, 4, 5
range(0, 10, 2)   # 0, 2, 4, 6, 8
range(10, 0, -1)  # 10, 9, 8, 7, 6, 5, 4, 3, 2, 1
```

### 2.3 `enumerate()` — Index + Value

```python
fruits = ["apple", "banana", "cherry"]

# BAD — using index manually
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# GOOD — use enumerate
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Start from 1
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}: {fruit}")
```

### 2.4 `zip()` — Parallel Iteration

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}")

# Unequal lengths — stops at shortest
ages = [25, 30]
for name, age in zip(names, ages):
    print(f"{name}: {age}")  # Only Alice and Bob
```

### 2.5 The `while` Loop

```python
count = 0
while count < 5:
    print(count)
    count += 1

# Infinite loop pattern
while True:
    user_input = input("Enter command (q to quit): ")
    if user_input == "q":
        break
    process(user_input)
```

#### ⚠️ Common Mistake: Infinite Loops

```python
# WRONG — forgot to increment!
i = 0
while i < 10:
    print(i)
    # i += 1  <-- Missing!

# WRONG — condition never becomes False
items = [1, 2, 3]
while items:
    print(items[0])
    # items.pop()  <-- Missing!
```

---

## 3. Loop Control

### 3.1 `break` — Exit Loop Immediately

```python
for num in range(100):
    if num == 5:
        break
    print(num)  # Prints 0, 1, 2, 3, 4
```

### 3.2 `continue` — Skip to Next Iteration

```python
for num in range(5):
    if num == 2:
        continue
    print(num)  # Prints 0, 1, 3, 4 (skips 2)
```

### 3.3 `else` on Loops — Executed If No `break`

```python
# The else runs if loop completes without break
for num in range(10):
    if num == 15:  # Never true
        break
else:
    print("Loop completed normally")  # This prints

# The else does NOT run if we break
for num in range(10):
    if num == 5:
        break
else:
    print("Loop completed normally")  # This does NOT print
```

#### 🧠 Engineering Thinking: When to Use Loop Else

```python
# Pattern: Search with fallback
def find_user(users, target_id):
    for user in users:
        if user["id"] == target_id:
            return user
    else:
        return None  # Not found

# Pattern: Validate all items
for item in items:
    if not is_valid(item):
        print("Invalid item found!")
        break
else:
    print("All items valid!")
```

---

## 4. Comprehensions

### 4.1 List Comprehension

```python
# Traditional
squares = []
for x in range(5):
    squares.append(x ** 2)

# Comprehension (Pythonic)
squares = [x ** 2 for x in range(5)]

# With condition
evens = [x for x in range(10) if x % 2 == 0]

# With transformation + condition
even_squares = [x ** 2 for x in range(10) if x % 2 == 0]
```

### 4.2 Dictionary Comprehension

```python
# Create dict from lists
names = ["a", "b", "c"]
values = [1, 2, 3]
d = {k: v for k, v in zip(names, values)}

# Transform dict
prices = {"apple": 1.0, "banana": 0.5}
doubled = {k: v * 2 for k, v in prices.items()}

# Filter dict
expensive = {k: v for k, v in prices.items() if v > 0.6}
```

### 4.3 Set Comprehension

```python
# Unique squares only
nums = [1, 2, 2, 3, 3, 3]
unique_squares = {x ** 2 for x in nums}  # {1, 4, 9}
```

#### ✅ Best Practice: Keep Comprehensions Simple

```python
# GOOD — simple and readable
squares = [x ** 2 for x in range(10)]

# BAD — too complex
result = [
    transform(x)
    for x in data
    if condition1(x) and condition2(x)
    for y in nested(x)
    if another_condition(y)
]

# BETTER — use regular loops for complex logic
result = []
for x in data:
    if condition1(x) and condition2(x):
        for y in nested(x):
            if another_condition(y):
                result.append(transform(x))
```

---

## 5. Match/Case (Python 3.10+)

### 5.1 Basic Matching

```python
status = 404

match status:
    case 200:
        print("OK")
    case 404:
        print("Not Found")
    case 500:
        print("Server Error")
    case _:
        print("Unknown status")
```

### 5.2 Matching Multiple Values

```python
match status:
    case 200 | 201:
        print("Success")
    case 400 | 404 | 422:
        print("Client Error")
    case 500 | 502 | 503:
        print("Server Error")
    case _:
        print("Unknown")
```

### 5.3 Structural Pattern Matching (The Power Feature)

```python
# Match and extract from structures
command = {"action": "move", "x": 10, "y": 20}

match command:
    case {"action": "quit"}:
        print("Quitting")
    case {"action": "move", "x": x, "y": y}:
        print(f"Moving to ({x}, {y})")  # Extracts x=10, y=20
    case {"action": "attack", "target": target}:
        print(f"Attacking {target}")
    case _:
        print("Unknown command")
```

### 5.4 Matching with Guards

```python
point = (10, 20)

match point:
    case (x, y) if x == y:
        print(f"On diagonal: ({x}, {y})")
    case (x, y) if x > y:
        print(f"Above diagonal: ({x}, {y})")
    case (x, y):
        print(f"Below diagonal: ({x}, {y})")
```

### 5.5 Matching Types

```python
def process(value):
    match value:
        case str():
            print(f"String: {value}")
        case int() | float():
            print(f"Number: {value}")
        case list():
            print(f"List with {len(value)} items")
        case _:
            print(f"Unknown type: {type(value)}")
```

#### 🧠 Engineering Thinking: When to Use Match/Case

| Use Case                   | match/case?               |
| -------------------------- | ------------------------- |
| Simple value comparison    | ✅ Yes                    |
| Extracting from structures | ✅ Yes                    |
| Type-based dispatch        | ✅ Yes                    |
| Complex conditions         | ⚠️ Sometimes (use guards) |
| Simple if-else             | ❌ Overkill               |

---

## 6. Control Flow Patterns

### 6.1 Early Return (Guard Clauses)

```python
# BAD — deeply nested
def process_user(user):
    if user is not None:
        if user.is_active:
            if user.has_permission:
                # actual logic here
                do_something(user)

# GOOD — early returns
def process_user(user):
    if user is None:
        return
    if not user.is_active:
        return
    if not user.has_permission:
        return

    # actual logic here (no nesting!)
    do_something(user)
```

### 6.2 Flag Variable Pattern

```python
# Track if something happened in a loop
found_error = False
for item in items:
    if is_invalid(item):
        found_error = True
        log_error(item)

if found_error:
    alert_admin()
```

### 6.3 Sentinel Loop Pattern

```python
# Process until special value
while True:
    line = input("Enter data (DONE to finish): ")
    if line == "DONE":
        break
    process(line)
```

### 6.4 Accumulator Pattern

```python
# Build up a result
total = 0
for num in numbers:
    total += num

# Or use sum()
total = sum(numbers)
```

---

## Common Anti-Patterns

### ❌ Comparing Booleans to True/False

```python
# WRONG
if is_valid == True:
    pass
if done == False:
    pass

# RIGHT
if is_valid:
    pass
if not done:
    pass
```

### ❌ Using `len()` to Check Empty

```python
# WRONG (but works)
if len(items) > 0:
    pass
if len(items) == 0:
    pass

# RIGHT (Pythonic)
if items:
    pass
if not items:
    pass
```

### ❌ Using Range + Index

```python
# WRONG
for i in range(len(items)):
    print(items[i])

# RIGHT
for item in items:
    print(item)

# RIGHT (when you need index)
for i, item in enumerate(items):
    print(i, item)
```

---

## Quick Reference

### Conditionals

```python
if x:              # Truthy check
if x is None:      # None check
if x == y:         # Equality
a if cond else b   # Ternary
```

### Loops

```python
for x in iterable:     # Iterate
for i in range(n):     # Count
for i, x in enumerate(lst):  # Index + value
for a, b in zip(x, y):  # Parallel
while condition:       # Conditional loop
```

### Control

```python
break      # Exit loop
continue   # Skip iteration
else:      # After loop (if no break)
```

### Comprehensions

```python
[x for x in lst]           # List
[x for x in lst if cond]   # Filtered
{k: v for k, v in items}   # Dict
{x for x in lst}           # Set
```

---

## Summary

You've learned:

1. **if-elif-else** — order matters (most specific first)
2. **Loops** — for, while, and their control keywords
3. **enumerate() and zip()** — cleaner iteration
4. **Comprehensions** — Pythonic one-liners
5. **match/case** — structural pattern matching
6. **Patterns** — early return, guards, accumulators

Next chapter: Functions & Scope — organizing code into reusable units.
