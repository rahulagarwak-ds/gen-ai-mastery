# Chapter 2: ruff — Lightning-Fast Linter & Formatter

> _"ruff replaces flake8, isort, black, and more — in milliseconds."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Why ruff is replacing traditional linting tools
- Configuring ruff for your projects
- Linting and auto-fixing code
- Formatting with ruff format
- Integrating with VS Code and CI/CD

---

## 1. Why ruff?

### The Old Way (Multiple Tools)

```bash
pip install flake8 black isort pylint mypy
# 5 config files, 5 different speeds, conflicts
```

### The ruff Way

```bash
uv add --dev ruff
# One tool, one config, 10-100x faster
```

### Speed Comparison

| Tool     | Time for 1000 files |
| -------- | ------------------- |
| flake8   | ~30 seconds         |
| pylint   | ~60 seconds         |
| **ruff** | **~0.3 seconds**    |

---

## 2. Installation

```bash
# With uv
uv add --dev ruff

# Or standalone
pip install ruff
```

---

## 3. Basic Usage

### Check for Issues

```bash
ruff check .
```

### Auto-Fix Issues

```bash
ruff check --fix .
```

### Format Code

```bash
ruff format .
```

### Check Without Changing

```bash
ruff format --check .
```

---

## 4. Configuration

Configure in `pyproject.toml`:

```toml
[tool.ruff]
# Target Python version
target-version = "py311"

# Line length
line-length = 88

# Exclude directories
exclude = [
    ".venv",
    "migrations",
    "__pycache__",
]

[tool.ruff.lint]
# Enable rule sets
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "SIM",    # flake8-simplify
]

# Ignore specific rules
ignore = [
    "E501",   # line too long (handled by formatter)
]

# Allow autofix for all enabled rules
fixable = ["ALL"]

[tool.ruff.lint.isort]
# Import sorting config
known-first-party = ["my_project"]

[tool.ruff.format]
# Use double quotes
quote-style = "double"
# Indent with spaces
indent-style = "space"
```

---

## 5. Rule Categories

### Essential Rules

| Code | Category    | Description                |
| ---- | ----------- | -------------------------- |
| E    | pycodestyle | Style errors               |
| W    | pycodestyle | Style warnings             |
| F    | pyflakes    | Logical errors             |
| I    | isort       | Import sorting             |
| B    | bugbear     | Bug risk patterns          |
| UP   | pyupgrade   | Python upgrade suggestions |

### Recommended Additional Rules

| Code | Category       | What it catches          |
| ---- | -------------- | ------------------------ |
| C4   | comprehensions | Unnecessary list() calls |
| SIM  | simplify       | Overly complex code      |
| PTH  | pathlib        | os.path vs pathlib       |
| RUF  | ruff-specific  | Ruff's own rules         |
| N    | pep8-naming    | Naming conventions       |

### Example Violations

```python
# F401: imported but unused
import os  # ruff will flag this

# I001: unsorted imports
import sys
import os  # Should be before sys

# B006: mutable default argument
def func(items=[]):  # Dangerous!
    pass

# SIM102: nested if can be collapsed
if a:
    if b:  # Can be: if a and b:
        pass
```

---

## 6. Common Workflows

### Check Before Commit

```bash
ruff check . && ruff format --check .
```

### Fix Everything

```bash
ruff check --fix . && ruff format .
```

### Check Single File

```bash
ruff check path/to/file.py
```

### Show What Would Change

```bash
ruff format --diff .
```

---

## 7. VS Code Integration

### Install Extension

1. Search for "Ruff" in VS Code extensions
2. Install the official Ruff extension

### Settings (settings.json)

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  },
  "ruff.lint.run": "onSave"
}
```

---

## 8. CI/CD Integration

### GitHub Actions

```yaml
name: Lint
on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
        with:
          args: 'check'
      - uses: astral-sh/ruff-action@v1
        with:
          args: 'format --check'
```

---

## 9. Per-File Ignores

Sometimes you need to ignore rules for specific files:

```toml
[tool.ruff.lint.per-file-ignores]
# Tests can use assert
"tests/**/*.py" = ["S101"]
# __init__ can have unused imports
"__init__.py" = ["F401"]
# Migrations have long lines
"migrations/*.py" = ["E501"]
```

---

## 10. Inline Ignores

```python
# Ignore specific line
x = 1  # noqa: E501

# Ignore specific rule for block
# ruff: noqa: F401
import unused_module

# Ignore entire file (at top)
# ruff: noqa
```

---

## Quick Reference

### Commands

```bash
ruff check .              # Lint
ruff check --fix .        # Lint + autofix
ruff format .             # Format
ruff format --check .     # Check formatting
ruff rule E501            # Explain a rule
```

### Recommended Config

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "SIM"]
```

---

## Summary

You've learned:

1. **Why ruff** — replaces multiple tools, 100x faster
2. **Basic usage** — check, fix, format
3. **Configuration** — rule selection, ignores
4. **VS Code** — format on save
5. **CI/CD** — GitHub Actions integration

Next chapter: pytest — testing fundamentals.
