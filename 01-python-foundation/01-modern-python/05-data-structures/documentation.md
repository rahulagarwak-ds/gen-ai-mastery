# Chapter 5: Data Structures Deep Dive

> _"Choosing the right data structure is 90% of solving the problem."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Lists: methods, slicing, performance characteristics
- Dictionaries: internal workings, common patterns
- Sets: when and why to use them
- Tuples: immutability advantages
- Collections module: Counter, defaultdict, deque
- When to use which data structure

---

## Prerequisites

- Chapters 1-4: Fundamentals through Functions

---

## 1. Lists Deep Dive

### 1.1 List Methods

```python
items = [3, 1, 4, 1, 5, 9, 2, 6]

# Adding elements
items.append(7)          # Add to end: [3, 1, 4, 1, 5, 9, 2, 6, 7]
items.insert(0, 0)       # Insert at index: [0, 3, 1, 4, ...]
items.extend([8, 9])     # Add multiple: [..., 7, 8, 9]

# Removing elements
items.pop()              # Remove & return last
items.pop(0)             # Remove & return at index
items.remove(1)          # Remove first occurrence of value
items.clear()            # Remove all

# Finding elements
items = [3, 1, 4, 1, 5]
items.index(4)           # 2 (first occurrence)
items.count(1)           # 2 (occurrences)

# Sorting
items.sort()             # In-place: [1, 1, 3, 4, 5]
items.sort(reverse=True) # Descending: [5, 4, 3, 1, 1]
items.reverse()          # In-place reverse

# Non-mutating alternatives
sorted_copy = sorted(items)  # Returns new list
reversed_copy = list(reversed(items))
```

### 1.2 List Slicing (Advanced)

```python
nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Basic slicing
nums[2:5]     # [2, 3, 4]
nums[:3]      # [0, 1, 2]
nums[7:]      # [7, 8, 9]
nums[::2]     # [0, 2, 4, 6, 8] (every 2nd)
nums[::-1]    # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (reversed)

# Negative indices
nums[-3:]     # [7, 8, 9] (last 3)
nums[:-3]     # [0, 1, 2, 3, 4, 5, 6] (all but last 3)

# Slice assignment
nums[2:5] = [20, 30, 40]  # Replace range
nums[2:2] = [99]          # Insert without removing
```

### 1.3 List Performance

| Operation      | Time Complexity | Notes            |
| -------------- | --------------- | ---------------- |
| `append()`     | O(1)            | Fast             |
| `pop()`        | O(1)            | From end         |
| `pop(0)`       | O(n)            | Slow! Use deque  |
| `insert(0, x)` | O(n)            | Slow!            |
| `x in list`    | O(n)            | Use set for O(1) |
| `index(x)`     | O(n)            | Linear search    |

#### 🧠 Engineering Thinking: When Lists Are Wrong

```python
# BAD — O(n) membership check, n times = O(n²)
valid_ids = [1, 2, 3, 4, 5, ..., 10000]
for user_id in incoming_ids:
    if user_id in valid_ids:  # O(n) each time!
        process(user_id)

# GOOD — O(1) membership check
valid_ids = {1, 2, 3, 4, 5, ..., 10000}  # Set!
for user_id in incoming_ids:
    if user_id in valid_ids:  # O(1)!
        process(user_id)
```

---

## 2. Dictionaries Deep Dive

### 2.1 Dict Methods

```python
user = {"name": "Alice", "age": 30, "city": "NYC"}

# Access
user["name"]              # "Alice" (KeyError if missing)
user.get("name")          # "Alice" (None if missing)
user.get("email", "N/A")  # "N/A" (custom default)

# Modification
user["email"] = "a@b.com" # Add/update
user.update({"age": 31, "role": "admin"})  # Bulk update
del user["city"]          # Remove key

# Safe removal
email = user.pop("email", None)  # Remove & return (or default)

# Views
user.keys()    # dict_keys(['name', 'age', 'role'])
user.values()  # dict_values(['Alice', 31, 'admin'])
user.items()   # dict_items([('name', 'Alice'), ...])

# Iteration
for key in user:
    print(key, user[key])

for key, value in user.items():
    print(f"{key}: {value}")
```

### 2.2 Dict Patterns

#### Default Value Pattern

```python
# BAD — verbose
if key not in data:
    data[key] = []
data[key].append(item)

# GOOD — setdefault
data.setdefault(key, []).append(item)

# BETTER — defaultdict (see Collections section)
```

#### Merge Dicts (Python 3.9+)

```python
defaults = {"timeout": 30, "retries": 3}
custom = {"timeout": 60}

# Merge (later wins)
config = defaults | custom  # {"timeout": 60, "retries": 3}

# Update in-place
defaults |= custom
```

### 2.3 Dict Comprehensions

```python
# Basic
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# From lists
names = ["alice", "bob"]
ages = [30, 25]
users = {n: a for n, a in zip(names, ages)}

# Filtered
high_scores = {k: v for k, v in scores.items() if v > 80}

# Swap keys/values
inverted = {v: k for k, v in original.items()}
```

### 2.4 Dict Performance

| Operation      | Time Complexity |
| -------------- | --------------- |
| `d[key]`       | O(1) average    |
| `d[key] = val` | O(1) average    |
| `key in d`     | O(1) average    |
| `del d[key]`   | O(1) average    |

Dicts are hash tables. Keys must be **hashable** (immutable).

```python
# Hashable (can be keys)
d = {
    "string": 1,
    42: 2,
    (1, 2): 3,      # Tuple
    frozenset({1}): 4,
}

# NOT hashable (cannot be keys)
d = {
    [1, 2]: 1,      # TypeError! List is mutable
    {1, 2}: 2,      # TypeError! Set is mutable
}
```

---

## 3. Sets Deep Dive

### 3.1 Set Basics

```python
# Creation
s = {1, 2, 3}
s = set([1, 2, 2, 3])  # {1, 2, 3} — duplicates removed

# Empty set (not {} which is empty dict!)
empty = set()

# Methods
s.add(4)          # Add element
s.remove(4)       # Remove (KeyError if missing)
s.discard(4)      # Remove (no error if missing)
s.pop()           # Remove & return arbitrary element
```

### 3.2 Set Operations

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}

# Union (or)
a | b             # {1, 2, 3, 4, 5, 6}
a.union(b)

# Intersection (and)
a & b             # {3, 4}
a.intersection(b)

# Difference
a - b             # {1, 2}
a.difference(b)

# Symmetric difference (xor)
a ^ b             # {1, 2, 5, 6}
a.symmetric_difference(b)

# Subset/superset
{1, 2} <= {1, 2, 3}  # True (subset)
{1, 2, 3} >= {1, 2}  # True (superset)
```

### 3.3 When to Use Sets

| Use Case                | Why Sets?             |
| ----------------------- | --------------------- |
| Remove duplicates       | `list(set(items))`    |
| Membership testing      | O(1) vs O(n) for list |
| Finding common elements | `set_a & set_b`       |
| Finding differences     | `set_a - set_b`       |

```python
# Practical: Find users in both lists
active = {"alice", "bob", "charlie"}
premium = {"bob", "diana", "eve"}

# Premium AND active
premium & active  # {"bob"}

# Premium but NOT active
premium - active  # {"diana", "eve"}
```

---

## 4. Tuples Deep Dive

### 4.1 Tuple Basics

Immutable sequences — once created, cannot be changed.

```python
# Creation
point = (10, 20)
single = (42,)   # Note the comma!
empty = ()

# Access (same as list)
point[0]         # 10
point[-1]        # 20

# Unpacking
x, y = point
a, b, c = (1, 2, 3)

# Extended unpacking
first, *rest = (1, 2, 3, 4, 5)  # first=1, rest=[2,3,4,5]
first, *middle, last = (1, 2, 3, 4, 5)  # middle=[2,3,4]
```

### 4.2 Why Tuples?

1. **Hashable** — can be dict keys or set members
2. **Signal intent** — "this data shouldn't change"
3. **Slightly faster** — less overhead than lists
4. **Named tuples** — structured data

```python
# Tuple as dict key
locations = {
    (40.7128, -74.0060): "New York",
    (34.0522, -118.2437): "Los Angeles",
}

# Structured data with namedtuple
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
```

---

## 5. The Collections Module

### 5.1 Counter

Count occurrences of elements.

```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counts = Counter(words)
# Counter({'apple': 3, 'banana': 2, 'cherry': 1})

counts.most_common(2)  # [('apple', 3), ('banana', 2)]
counts["apple"]        # 3
counts["missing"]      # 0 (no KeyError!)

# Arithmetic
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
c1 + c2  # Counter({'a': 4, 'b': 3})
c1 - c2  # Counter({'a': 2}) (no negative counts)
```

### 5.2 defaultdict

Dict with automatic default values.

```python
from collections import defaultdict

# Group items by category
items = [
    ("fruit", "apple"),
    ("vegetable", "carrot"),
    ("fruit", "banana"),
    ("vegetable", "broccoli"),
]

# Without defaultdict
groups = {}
for category, item in items:
    if category not in groups:
        groups[category] = []
    groups[category].append(item)

# With defaultdict
groups = defaultdict(list)
for category, item in items:
    groups[category].append(item)

# Result: {'fruit': ['apple', 'banana'], 'vegetable': ['carrot', 'broccoli']}
```

### 5.3 deque (Double-Ended Queue)

O(1) operations on both ends.

```python
from collections import deque

q = deque([1, 2, 3])

# O(1) operations on both ends
q.append(4)       # Right: [1, 2, 3, 4]
q.appendleft(0)   # Left: [0, 1, 2, 3, 4]
q.pop()           # Right: returns 4
q.popleft()       # Left: returns 0

# Fixed-size buffer
recent = deque(maxlen=3)
recent.append(1)  # [1]
recent.append(2)  # [1, 2]
recent.append(3)  # [1, 2, 3]
recent.append(4)  # [2, 3, 4] — oldest dropped
```

### 5.4 OrderedDict

Dict that remembers insertion order (Python 3.7+ dicts do this by default, but OrderedDict has extra methods).

```python
from collections import OrderedDict

od = OrderedDict()
od["first"] = 1
od["second"] = 2
od.move_to_end("first")  # Move to end
od.popitem(last=False)   # Pop first item
```

---

## 6. Choosing the Right Data Structure

| Need                        | Use                 | Reason           |
| --------------------------- | ------------------- | ---------------- |
| Ordered, mutable collection | `list`              | General purpose  |
| Fast membership testing     | `set`               | O(1) lookup      |
| Key-value mapping           | `dict`              | O(1) access      |
| Immutable sequence          | `tuple`             | Hashable, safe   |
| Counting                    | `Counter`           | Built-in counts  |
| Grouping                    | `defaultdict(list)` | Auto-create keys |
| Queue operations            | `deque`             | O(1) both ends   |

---

## ⚠️ Common Mistakes

### Modifying List While Iterating

```python
# WRONG — skips elements!
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)

# CORRECT — iterate over copy
for item in items[:]:  # or list(items)
    if item % 2 == 0:
        items.remove(item)

# BETTER — use comprehension
items = [item for item in items if item % 2 != 0]
```

### Using List for Membership

```python
# SLOW — O(n) per check
if user_id in user_list:  # DON'T DO THIS

# FAST — O(1) per check
if user_id in user_set:   # DO THIS
```

---

## Quick Reference

### List

```python
lst.append(x)    lst.pop()    lst.sort()
lst.extend(x)    lst.remove(x)    sorted(lst)
```

### Dict

```python
d.get(k, default)    d.keys()    d.items()
d.setdefault(k, v)   d.pop(k)    d.update(other)
```

### Set

```python
a | b    a & b    a - b    a ^ b
a.add(x)    a.remove(x)    a.discard(x)
```

### Collections

```python
Counter(iterable)    defaultdict(list)    deque([])
```

---

## Summary

You've learned:

1. **Lists**: methods, slicing, performance pitfalls
2. **Dicts**: patterns, comprehensions, hash requirements
3. **Sets**: operations, O(1) membership
4. **Tuples**: immutability, hashability
5. **Collections**: Counter, defaultdict, deque
6. **Choosing wisely**: match structure to use case

Next chapter: Object-Oriented Programming — classes, inheritance, and design.
