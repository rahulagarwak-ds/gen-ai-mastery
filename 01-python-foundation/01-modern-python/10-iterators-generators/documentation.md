# Chapter 10: Iterators & Generators

> _"Why load a million rows into memory when you only need to process one at a time?"_

---

## What You'll Learn

By the end of this chapter, you will understand:

- The iterator protocol
- Creating custom iterators
- Generator functions with `yield`
- Generator expressions
- Memory-efficient data processing
- The itertools module
- Async generators (intro)

---

## Prerequisites

- Chapters 1-9: All previous content

---

## 1. The Iterator Protocol

### 1.1 What is an Iterator?

An iterator is an object that:

1. Implements `__iter__()` — returns itself
2. Implements `__next__()` — returns next value or raises `StopIteration`

```python
# Lists are iterable, not iterators
numbers = [1, 2, 3]

# Get iterator from iterable
iterator = iter(numbers)

# Get values one at a time
print(next(iterator))  # 1
print(next(iterator))  # 2
print(next(iterator))  # 3
print(next(iterator))  # StopIteration!
```

### 1.2 How `for` Loops Work

```python
# This:
for item in [1, 2, 3]:
    print(item)

# Is equivalent to:
iterator = iter([1, 2, 3])
while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

### 1.3 Custom Iterator Class

```python
class CountDown:
    """Count down from n to 1."""

    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

# Usage
for num in CountDown(5):
    print(num)  # 5, 4, 3, 2, 1
```

---

## 2. Generators

Simpler way to create iterators — functions that `yield` values.

### 2.1 Basic Generator Function

```python
def count_down(start: int):
    """Yield numbers from start down to 1."""
    current = start
    while current > 0:
        yield current
        current -= 1

# Usage
for num in count_down(5):
    print(num)  # 5, 4, 3, 2, 1

# Generator is an iterator
gen = count_down(3)
print(next(gen))  # 3
print(next(gen))  # 2
print(next(gen))  # 1
print(next(gen))  # StopIteration
```

### 2.2 How Generators Work

```python
def simple_generator():
    print("Starting")
    yield 1
    print("After first yield")
    yield 2
    print("After second yield")
    yield 3
    print("Ending")

gen = simple_generator()
print(next(gen))
# Output:
# Starting
# 1

print(next(gen))
# Output:
# After first yield
# 2
```

The function **pauses** at each `yield` and **resumes** on `next()`.

### 2.3 Generator Expressions

Like list comprehensions, but lazy.

```python
# List comprehension — creates list in memory
squares_list = [x**2 for x in range(1000000)]

# Generator expression — creates generator (lazy)
squares_gen = (x**2 for x in range(1000000))

# Memory usage:
import sys
print(sys.getsizeof(squares_list))  # ~8 MB
print(sys.getsizeof(squares_gen))   # ~120 bytes!
```

---

## 3. Practical Generator Patterns

### 3.1 Reading Large Files

```python
def read_lines(filepath: str):
    """Read file line by line without loading all."""
    with open(filepath) as f:
        for line in f:
            yield line.strip()

# Process millions of lines with constant memory
for line in read_lines("huge_file.txt"):
    process(line)
```

### 3.2 Infinite Generators

```python
def count_forever(start: int = 0):
    """Count up forever."""
    n = start
    while True:
        yield n
        n += 1

# Use with islice to limit
from itertools import islice
first_10 = list(islice(count_forever(), 10))
# [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### 3.3 Generator Pipeline

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line

def parse_json(lines):
    import json
    for line in lines:
        yield json.loads(line)

def filter_active(records):
    for record in records:
        if record.get("active"):
            yield record

# Pipeline — each step is lazy
lines = read_lines("data.jsonl")
records = parse_json(lines)
active = filter_active(records)

# Nothing happens until we consume
for record in active:
    process(record)
```

### 3.4 yield from — Delegate to Sub-Generator

```python
def flatten(nested):
    """Flatten nested lists."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)  # Delegate to recursive call
        else:
            yield item

list(flatten([1, [2, [3, 4]], 5]))
# [1, 2, 3, 4, 5]
```

---

## 4. The itertools Module

Powerful tools for working with iterators.

### 4.1 Infinite Iterators

```python
from itertools import count, cycle, repeat

# Count forever
for n in count(10, 2):  # 10, 12, 14, 16, ...
    if n > 20:
        break

# Cycle through elements
colors = cycle(["red", "green", "blue"])
for _ in range(5):
    print(next(colors))  # red, green, blue, red, green

# Repeat value
list(repeat("hello", 3))  # ["hello", "hello", "hello"]
```

### 4.2 Combinatoric Iterators

```python
from itertools import product, permutations, combinations

# Cartesian product
list(product([1, 2], ["a", "b"]))
# [(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]

# Permutations
list(permutations([1, 2, 3], 2))
# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

# Combinations
list(combinations([1, 2, 3], 2))
# [(1, 2), (1, 3), (2, 3)]
```

### 4.3 Selection and Slicing

```python
from itertools import islice, takewhile, dropwhile, filterfalse

nums = range(10)

# Take first n
list(islice(nums, 5))  # [0, 1, 2, 3, 4]

# Take while condition is true
list(takewhile(lambda x: x < 5, nums))  # [0, 1, 2, 3, 4]

# Drop while condition is true
list(dropwhile(lambda x: x < 5, nums))  # [5, 6, 7, 8, 9]

# Filter out truthy (opposite of filter)
list(filterfalse(lambda x: x % 2, nums))  # [0, 2, 4, 6, 8]
```

### 4.4 Grouping and Aggregating

```python
from itertools import groupby, accumulate, chain

# Group consecutive equal elements
data = [("a", 1), ("a", 2), ("b", 3), ("b", 4)]
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# a [('a', 1), ('a', 2)]
# b [('b', 3), ('b', 4)]

# Running sum
list(accumulate([1, 2, 3, 4, 5]))  # [1, 3, 6, 10, 15]

# Chain iterables
list(chain([1, 2], [3, 4], [5]))  # [1, 2, 3, 4, 5]
```

---

## 5. Memory Efficiency

### Comparison: List vs Generator

```python
import sys

# List — all in memory
numbers_list = [x**2 for x in range(1_000_000)]
print(f"List: {sys.getsizeof(numbers_list):,} bytes")
# List: 8,448,728 bytes

# Generator — lazy evaluation
numbers_gen = (x**2 for x in range(1_000_000))
print(f"Generator: {sys.getsizeof(numbers_gen)} bytes")
# Generator: 112 bytes
```

### When to Use Generators

| Scenario                | Use Generator?                   |
| ----------------------- | -------------------------------- |
| Processing large files  | ✅ Yes                           |
| Streaming API responses | ✅ Yes                           |
| Infinite sequences      | ✅ Yes                           |
| Need multiple passes    | ❌ No (exhausted after one pass) |
| Need random access      | ❌ No (sequential only)          |
| Need length             | ❌ No (unknown until exhausted)  |

---

## 6. Async Generators (Preview)

For async iteration (covered more in AsyncIO).

```python
async def async_count(n: int):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for num in async_count(5):
        print(num)
```

---

## Quick Reference

### Iterator Protocol

```python
class MyIterator:
    def __iter__(self):
        return self

    def __next__(self):
        # Return next value or raise StopIteration
        pass
```

### Generator Function

```python
def my_generator():
    yield value1
    yield value2
    yield from other_iterable
```

### Generator Expression

```python
gen = (x**2 for x in range(10))
```

### itertools Highlights

```python
islice(iterable, stop)
takewhile(pred, iterable)
dropwhile(pred, iterable)
chain(*iterables)
groupby(iterable, key=func)
```

---

## Summary

You've learned:

1. **Iterator protocol** — `__iter__` and `__next__`
2. **Generators** — functions with `yield`
3. **Generator expressions** — lazy comprehensions
4. **Pipelines** — compose generators for processing
5. **itertools** — powerful iteration tools
6. **Memory efficiency** — process millions without loading all

Next chapter: Dataclasses & Pydantic — structured data made easy.
