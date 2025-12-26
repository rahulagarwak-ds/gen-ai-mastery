# Chapter 2: Strings & Formatting

> _"Every output your program produces is ultimately a string. Master strings, master communication."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- String internals and immutability
- All formatting methods (f-strings, format(), %)
- String methods every engineer must know
- Unicode and encoding (critical for real-world data)
- Regular expressions basics
- Performance considerations for string operations

---

## Prerequisites

- Chapter 1: Python Fundamentals
- Understanding of basic data types

---

## 1. String Fundamentals

### 1.1 Strings Are Immutable

Unlike lists, strings cannot be changed after creation. Every "modification" creates a new string.

```python
s = "hello"
s[0] = "H"  # TypeError: 'str' object does not support item assignment

# You must create a new string
s = "H" + s[1:]  # "Hello"
```

#### 🧠 Engineering Thinking: Memory Implications

```python
# BAD — creates many intermediate strings
result = ""
for i in range(10000):
    result += str(i)  # O(n²) — each += creates a new string

# GOOD — use join
parts = [str(i) for i in range(10000)]
result = "".join(parts)  # O(n) — single concatenation
```

### 1.2 String Creation

```python
# Single quotes or double quotes — no difference
s1 = 'hello'
s2 = "hello"
s1 == s2  # True

# Triple quotes for multiline
long_text = """
This is a
multiline string.
It preserves newlines.
"""

# Raw strings — backslashes are literal
path = r"C:\Users\name\folder"  # No escape interpretation
regex = r"\d+\.\d+"  # Easier to write regex
```

### 1.3 String Indexing and Slicing

```python
s = "Python"

# Indexing (0-based)
s[0]   # 'P'
s[-1]  # 'n' (last character)
s[-2]  # 'o' (second to last)

# Slicing: s[start:stop:step]
s[0:3]    # 'Pyt' (0, 1, 2)
s[3:]     # 'hon' (3 to end)
s[:3]     # 'Pyt' (start to 3)
s[::2]    # 'Pto' (every 2nd char)
s[::-1]   # 'nohtyP' (reversed)
```

#### ⚠️ Common Mistake: Off-by-One Errors

```python
s = "hello"

# The stop index is EXCLUSIVE
s[0:3]  # 'hel' — NOT 'hell'

# To get characters 1-3 (1, 2, 3), use:
s[1:4]  # 'ell'
```

---

## 2. String Formatting

### 2.1 F-Strings (Python 3.6+) — The Modern Way

F-strings are the fastest and most readable formatting method.

```python
name = "Alice"
age = 30
balance = 1234.567

# Basic interpolation
f"Hello, {name}!"  # "Hello, Alice!"

# Expressions inside braces
f"{name.upper()} is {age * 12} months old"  # "ALICE is 360 months old"

# Format specifications
f"Balance: ${balance:.2f}"      # "Balance: $1234.57"
f"Age: {age:05d}"               # "Age: 00030" (zero-padded)
f"Name: {name:>10}"             # "Name:      Alice" (right-aligned)
f"Name: {name:<10}"             # "Name: Alice     " (left-aligned)
f"Name: {name:^10}"             # "Name:   Alice  " (centered)
```

#### Format Specification Mini-Language

```
{value:[[fill]align][sign][#][0][width][grouping][.precision][type]}
```

| Spec   | Meaning                 | Example                          |
| ------ | ----------------------- | -------------------------------- |
| `:.2f` | 2 decimal places        | `f"{3.14159:.2f}"` → `"3.14"`    |
| `:05d` | 5 digits, zero-padded   | `f"{42:05d}"` → `"00042"`        |
| `:>10` | Right-align, width 10   | `f"{'hi':>10}"` → `"        hi"` |
| `:<10` | Left-align, width 10    | `f"{'hi':<10}"` → `"hi        "` |
| `:^10` | Center, width 10        | `f"{'hi':^10}"` → `"    hi    "` |
| `:,`   | Thousands separator     | `f"{1000000:,}"` → `"1,000,000"` |
| `:%`   | Percentage              | `f"{0.25:%}"` → `"25.000000%"`   |
| `:.0%` | Percentage, no decimals | `f"{0.25:.0%}"` → `"25%"`        |

#### Debug Mode (Python 3.8+)

```python
x = 42
y = "hello"

# The = suffix shows variable name and value
print(f"{x=}")       # "x=42"
print(f"{y=}")       # "y='hello'"
print(f"{x + 10=}")  # "x + 10=52"
```

### 2.2 The `.format()` Method

Older but still useful, especially for reusable templates.

```python
# Positional arguments
"{} and {}".format("Alice", "Bob")  # "Alice and Bob"

# Named arguments
"{name} is {age}".format(name="Alice", age=30)  # "Alice is 30"

# Index-based
"{0} vs {1}. {0} wins!".format("Python", "Java")  # "Python vs Java. Python wins!"

# Reusable template
template = "Hello, {name}! Your balance is ${balance:.2f}"
template.format(name="Alice", balance=1234.5)
template.format(name="Bob", balance=567.89)
```

### 2.3 Percent Formatting (Legacy)

You'll see this in old codebases. Know how to read it.

```python
"Hello, %s!" % "Alice"           # "Hello, Alice!"
"Age: %d, Score: %.2f" % (30, 95.5)  # "Age: 30, Score: 95.50"

# %s = string, %d = integer, %f = float, %% = literal %
```

#### ✅ Best Practice: Use F-Strings

```python
# AVOID — old style
"Hello, %s! You have %d messages." % (name, count)

# AVOID — verbose
"Hello, {}! You have {} messages.".format(name, count)

# PREFER — clear and fast
f"Hello, {name}! You have {count} messages."
```

---

## 3. Essential String Methods

### 3.1 Case Conversion

```python
s = "Hello World"

s.lower()      # "hello world"
s.upper()      # "HELLO WORLD"
s.title()      # "Hello World"
s.capitalize() # "Hello world"
s.swapcase()   # "hELLO wORLD"
s.casefold()   # "hello world" (aggressive lowercase for comparison)
```

### 3.2 Searching

```python
s = "hello world, hello python"

# Find position (-1 if not found)
s.find("world")       # 6
s.find("java")        # -1
s.rfind("hello")      # 13 (last occurrence)

# Index (raises ValueError if not found)
s.index("world")      # 6
# s.index("java")     # ValueError!

# Count occurrences
s.count("hello")      # 2
s.count("l")          # 5

# Check existence
"world" in s          # True
s.startswith("hello") # True
s.endswith("python")  # True
```

#### ⚠️ Common Mistake: Using `find()` Without Checking

```python
s = "hello world"

# WRONG — position 0 is truthy, but so is finding at start
pos = s.find("hello")
if pos:  # 0 is falsy! This won't work for matches at position 0
    print("Found")

# CORRECT — explicitly check for -1
pos = s.find("hello")
if pos != -1:
    print("Found at position", pos)

# EVEN BETTER — use 'in' for existence checks
if "hello" in s:
    print("Found")
```

### 3.3 Splitting and Joining

```python
# Split
"a,b,c".split(",")           # ['a', 'b', 'c']
"a b  c".split()             # ['a', 'b', 'c'] (default: any whitespace)
"a,b,c".split(",", maxsplit=1)  # ['a', 'b,c']

# Splitlines
"line1\nline2\nline3".splitlines()  # ['line1', 'line2', 'line3']

# Join (opposite of split)
",".join(["a", "b", "c"])    # "a,b,c"
" | ".join(["x", "y", "z"])  # "x | y | z"
"".join(["a", "b", "c"])     # "abc"
```

### 3.4 Stripping Whitespace

```python
s = "  hello world  \n"

s.strip()   # "hello world"
s.lstrip()  # "hello world  \n"
s.rstrip()  # "  hello world"

# Strip specific characters
"...hello...".strip(".")  # "hello"
```

### 3.5 Replacing

```python
s = "hello world"

s.replace("world", "python")  # "hello python"
s.replace("l", "L")           # "heLLo worLd"
s.replace("l", "L", 1)        # "heLlo world" (max 1 replacement)
```

### 3.6 Checking Content

```python
# All characters match criteria
"123".isdigit()      # True
"abc".isalpha()      # True
"abc123".isalnum()   # True
"   ".isspace()      # True
"Hello".istitle()    # True
"HELLO".isupper()    # True
"hello".islower()    # True
```

---

## 4. Unicode and Encoding

### 4.1 Unicode Basics

Python 3 strings are Unicode by default. Each character is a Unicode code point.

```python
# Any Unicode character
emoji = "🐍"
chinese = "你好"
mixed = "Hello 世界 🌍"

len(emoji)    # 1 (one code point)
len(chinese)  # 2
len(mixed)    # 12
```

### 4.2 Encoding and Decoding

Encoding: String → Bytes (for storage/transmission)
Decoding: Bytes → String (for processing)

```python
# Encoding
text = "Hello 世界"
encoded = text.encode("utf-8")  # b'Hello \xe4\xb8\x96\xe7\x95\x8c'

# Decoding
decoded = encoded.decode("utf-8")  # "Hello 世界"
```

#### ⚠️ Common Mistake: Wrong Encoding

```python
text = "Héllo"

# Encode with utf-8
encoded = text.encode("utf-8")  # b'H\xc3\xa9llo'

# WRONG — decode with wrong encoding
encoded.decode("ascii")  # UnicodeDecodeError!

# CORRECT — use same encoding
encoded.decode("utf-8")  # "Héllo"
```

#### 🧠 Engineering Thinking: Always Specify Encoding

```python
# WRONG — uses system default (varies!)
with open("data.txt") as f:
    content = f.read()

# CORRECT — explicit encoding
with open("data.txt", encoding="utf-8") as f:
    content = f.read()
```

### 4.3 Common Encodings

| Encoding  | Use Case                                 |
| --------- | ---------------------------------------- |
| `utf-8`   | Default for web, files, APIs (use this!) |
| `ascii`   | Legacy systems, English-only             |
| `latin-1` | Western European                         |
| `utf-16`  | Windows internal, some APIs              |

---

## 5. Regular Expressions Basics

For pattern matching beyond simple `find()` and `in`.

```python
import re

text = "Contact: alice@example.com, bob@test.org"

# Search for pattern
match = re.search(r"\w+@\w+\.\w+", text)
if match:
    print(match.group())  # "alice@example.com"

# Find all matches
emails = re.findall(r"\w+@\w+\.\w+", text)
print(emails)  # ['alice@example.com', 'bob@test.org']

# Replace with pattern
cleaned = re.sub(r"\w+@\w+\.\w+", "[EMAIL]", text)
print(cleaned)  # "Contact: [EMAIL], [EMAIL]"
```

### Common Patterns

| Pattern | Matches         | Example                     |
| ------- | --------------- | --------------------------- |
| `\d`    | Digit           | `\d+` matches "123"         |
| `\w`    | Word char       | `\w+` matches "hello_123"   |
| `\s`    | Whitespace      | `\s+` matches " "           |
| `.`     | Any char        | `a.c` matches "abc"         |
| `*`     | 0 or more       | `a*` matches "", "a", "aaa" |
| `+`     | 1 or more       | `a+` matches "a", "aaa"     |
| `?`     | 0 or 1          | `a?` matches "", "a"        |
| `[]`    | Character class | `[aeiou]` matches vowels    |
| `^`     | Start           | `^Hello` matches start      |
| `$`     | End             | `world$` matches end        |

---

## 6. Performance Considerations

### 6.1 String Concatenation

```python
# BAD — O(n²) for large loops
result = ""
for word in words:
    result += word + " "

# GOOD — O(n)
result = " ".join(words)
```

### 6.2 String Interning

Python caches small strings for efficiency.

```python
a = "hello"
b = "hello"
print(a is b)  # True — same object

c = "hello world this is long"
d = "hello world this is long"
print(c is d)  # Maybe True, maybe False (implementation-dependent)
```

#### ✅ Best Practice: Never Rely on Interning

Always use `==` for string comparison, never `is`.

---

## Quick Reference

### Formatting Cheat Sheet

```python
f"{value:.2f}"      # 2 decimals
f"{value:,}"        # Thousands separator
f"{value:>10}"      # Right-align
f"{value:<10}"      # Left-align
f"{value:^10}"      # Center
f"{value:05d}"      # Zero-pad
f"{value=}"         # Debug mode
```

### Common Operations

```python
s.strip()           # Remove whitespace
s.split(",")        # Split to list
",".join(lst)       # Join list to string
s.replace(a, b)     # Replace occurrences
s.lower() / upper() # Case conversion
s.startswith(x)     # Check prefix
s.endswith(x)       # Check suffix
```

---

## Summary

You've learned:

1. **Strings are immutable** — use `join()` for efficient concatenation
2. **F-strings** — the modern, fast, readable way to format
3. **Essential methods** — split, join, strip, replace, find
4. **Unicode** — always specify `encoding="utf-8"`
5. **Regex basics** — for pattern matching
6. **Performance** — avoid `+=` in loops

Next chapter: Control Flow — making decisions and repeating actions.
