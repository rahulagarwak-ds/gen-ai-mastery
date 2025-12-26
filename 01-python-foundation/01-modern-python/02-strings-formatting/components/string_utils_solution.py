"""
String Utilities Module

Production-ready string manipulation utilities.
Common patterns used across Gen AI applications.
"""

import re
from typing import Any


def clean_text(text: str) -> str:
    """
    Clean text by stripping and collapsing whitespace.
    
    Example:
        >>> clean_text("  Hello    World  ")
        'Hello World'
    """
    return " ".join(text.split())


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max_length, adding suffix if truncated.
    
    Example:
        >>> truncate("Hello World", 8)
        'Hello...'
        >>> truncate("Hi", 10)
        'Hi'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug.
    
    Example:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("  Python 3.10 is GREAT  ")
        'python-3-10-is-great'
    """
    # Lowercase and strip
    text = text.lower().strip()
    # Replace non-alphanumeric with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


def extract_emails(text: str) -> list[str]:
    """
    Extract all email addresses from text.
    
    Example:
        >>> extract_emails("Contact alice@example.com or bob@test.org")
        ['alice@example.com', 'bob@test.org']
    """
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(pattern, text)


def mask_sensitive(text: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data, showing only last N characters.
    
    Example:
        >>> mask_sensitive("1234567890123456", 4)
        '************3456'
        >>> mask_sensitive("secret_api_key", 4)
        '**********_key'
    """
    if len(text) <= visible_chars:
        return "*" * len(text)
    return "*" * (len(text) - visible_chars) + text[-visible_chars:]


def format_currency(amount: float, symbol: str = "$", decimals: int = 2) -> str:
    """
    Format number as currency with thousands separator.
    
    Example:
        >>> format_currency(1234567.89)
        '$1,234,567.89'
        >>> format_currency(1234.5, "€", 2)
        '€1,234.50'
    """
    return f"{symbol}{amount:,.{decimals}f}"


def safe_format(template: str, **kwargs: Any) -> str:
    """
    Format string template, leaving missing keys as placeholders.
    
    Unlike str.format(), doesn't raise KeyError for missing keys.
    
    Example:
        >>> safe_format("Hello {name}, you have {count} messages", name="Alice")
        'Hello Alice, you have {count} messages'
    """
    class SafeDict(dict):
        def __missing__(self, key: str) -> str:
            return f"{{{key}}}"
    
    return template.format_map(SafeDict(**kwargs))


def split_into_chunks(text: str, chunk_size: int) -> list[str]:
    """
    Split text into chunks of specified size.
    
    Useful for processing large texts with LLMs that have token limits.
    
    Example:
        >>> split_into_chunks("Hello World", 4)
        ['Hell', 'o Wo', 'rld']
    """
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace (tabs, newlines) to single spaces.
    
    Example:
        >>> normalize_whitespace("Hello\\n\\tWorld")
        'Hello World'
    """
    return " ".join(text.split())


def remove_punctuation(text: str) -> str:
    """
    Remove all punctuation from text.
    
    Example:
        >>> remove_punctuation("Hello, World!")
        'Hello World'
    """
    return re.sub(r'[^\w\s]', '', text)


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case.
    
    Example:
        >>> to_snake_case("HelloWorld")
        'hello_world'
        >>> to_snake_case("getHTTPResponse")
        'get_http_response'
    """
    # Add underscore before uppercase letters
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', text)
    s2 = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s1)
    return s2.lower().replace(' ', '_').replace('-', '_')


def to_camel_case(text: str) -> str:
    """
    Convert text to camelCase.
    
    Example:
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("get-http-response")
        'getHttpResponse'
    """
    # Split on underscores or hyphens
    words = re.split(r'[-_]', text)
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


# === Tests ===
if __name__ == "__main__":
    assert clean_text("  Hello    World  ") == "Hello World"
    assert truncate("Hello World", 8) == "Hello..."
    assert truncate("Hi", 10) == "Hi"
    assert slugify("Hello World!") == "hello-world"
    assert extract_emails("Email: test@example.com") == ["test@example.com"]
    assert mask_sensitive("1234567890", 4) == "******7890"
    assert format_currency(1234.5) == "$1,234.50"
    assert safe_format("{a} and {b}", a="X") == "X and {b}"
    assert split_into_chunks("abcdefgh", 3) == ["abc", "def", "gh"]
    assert to_snake_case("HelloWorld") == "hello_world"
    assert to_camel_case("hello_world") == "helloWorld"
    
    print("✅ All tests passed!")
