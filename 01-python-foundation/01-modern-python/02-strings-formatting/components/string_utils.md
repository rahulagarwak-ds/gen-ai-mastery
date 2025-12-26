# Mini Project: String Utilities Module

## 🎯 Objective

Build a production-ready string utilities module with common text processing functions used in real applications.

---

## 📋 Requirements

### 1. Text Cleaning Functions

```python
def clean(text: str) -> str:
    """
    Clean text by stripping whitespace and normalizing spaces.
    Multiple spaces become single space.

    Example:
        clean("  hello   world  ")  # "hello world"
    """
    pass

def remove_punctuation(text: str) -> str:
    """Remove all punctuation from text."""
    pass

def normalize_whitespace(text: str) -> str:
    """Replace all whitespace (tabs, newlines, etc.) with single spaces."""
    pass
```

### 2. Text Transformation Functions

```python
def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Example:
        slugify("Hello World!")  # "hello-world"
        slugify("My Blog Post #1")  # "my-blog-post-1"
    """
    pass

def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max_length, adding suffix if truncated.
    Don't cut words in the middle.

    Example:
        truncate("Hello wonderful world", 15)  # "Hello..."
    """
    pass

def to_title_case(text: str) -> str:
    """
    Convert to title case handling edge cases.

    Example:
        to_title_case("hello world")  # "Hello World"
        to_title_case("the quick brown FOX")  # "The Quick Brown Fox"
    """
    pass
```

### 3. Pattern Extraction Functions

```python
def extract_emails(text: str) -> list[str]:
    """Extract all email addresses from text."""
    pass

def extract_urls(text: str) -> list[str]:
    """Extract all URLs from text."""
    pass

def extract_numbers(text: str) -> list[float]:
    """
    Extract all numbers (int or float) from text.

    Example:
        extract_numbers("Price: $19.99, Qty: 5")  # [19.99, 5.0]
    """
    pass
```

### 4. Masking Functions

```python
def mask_email(email: str) -> str:
    """
    Mask email for privacy.

    Example:
        mask_email("john.doe@example.com")  # "j***e@example.com"
    """
    pass

def mask_credit_card(number: str) -> str:
    """
    Mask credit card number.

    Example:
        mask_credit_card("4111111111111111")  # "****-****-****-1111"
    """
    pass
```

---

## ✅ Test Cases

```python
# Cleaning
assert clean("  hello   world  ") == "hello world"

# Slugify
assert slugify("Hello World!") == "hello-world"
assert slugify("Python 3.11 Released") == "python-3-11-released"

# Truncate
assert truncate("Hello wonderful world", 15) == "Hello..."
assert truncate("Hi", 10) == "Hi"  # No truncation needed

# Extract
assert extract_emails("Contact: a@b.com or c@d.org") == ["a@b.com", "c@d.org"]
assert extract_numbers("Total: $99.50, Items: 3") == [99.5, 3.0]

# Mask
assert mask_email("john.doe@gmail.com") == "j*****e@gmail.com"
```

---

## 🏆 Bonus Challenges

1. Add `format_currency(amount, locale)` with proper locale support
2. Add `highlight_matches(text, pattern)` that wraps matches in HTML
3. Add `word_wrap(text, width)` for terminal output

---

## 📁 Deliverable

Create `string_utils.py` with all functions, proper type hints, and docstrings.

**Time estimate:** 45-60 minutes

---

## 💡 Hints

<details>
<summary>Hint 1: Slugify</summary>

Use regex to remove special chars, replace spaces with hyphens, lowercase.

</details>

<details>
<summary>Hint 2: Truncate</summary>

Find the last space before max_length and cut there.

</details>
