# Chapter 5: Python Project Structure

> _"Good structure is invisible. You only notice when it's missing."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Modern Python project layouts
- The src layout pattern
- Organizing modules and packages
- Configuration file placement
- README and documentation standards

---

## 1. The src Layout (Recommended)

```
my-project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── services/
│       │   ├── __init__.py
│       │   └── auth.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── test_helpers.py
│   └── integration/
│       └── test_auth.py
├── .pre-commit-config.yaml
├── .python-version
├── pyproject.toml
├── README.md
└── uv.lock
```

### Why src Layout?

1. **Prevents import confusion** — Can't accidentally import uninstalled package
2. **Cleaner root** — Config files separate from code
3. **Professional standard** — Used by major projects

---

## 2. Key Files Explained

### pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Short description"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
    "pre-commit>=3.0",
]

[project.scripts]
my-cli = "my_project.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v"
```

### .python-version

```
3.11
```

### .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/

# Distribution
dist/
build/
*.egg-info/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
```

---

## 3. Module Organization

### Flat (Small Projects)

```
src/my_project/
├── __init__.py
├── main.py
├── models.py
└── utils.py
```

### Layered (Medium Projects)

```
src/my_project/
├── __init__.py
├── main.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── product.py
├── services/
│   ├── __init__.py
│   ├── auth.py
│   └── email.py
├── api/
│   ├── __init__.py
│   └── routes.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

### Domain-Driven (Large Projects)

```
src/my_project/
├── __init__.py
├── main.py
├── users/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── routes.py
├── products/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── routes.py
└── shared/
    ├── __init__.py
    ├── database.py
    └── auth.py
```

---

## 4. The **init**.py File

### Empty (Minimal)

```python
# Just marks directory as package
```

### With Public API

```python
# src/my_project/__init__.py
"""My Project - Does amazing things."""

from my_project.models import User, Product
from my_project.services import process

__version__ = "0.1.0"

__all__ = ["User", "Product", "process", "__version__"]
```

### Usage

```python
# Clean imports for users
from my_project import User, process
```

---

## 5. Test Organization

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── unit/                 # Fast, isolated tests
│   ├── __init__.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/          # Tests with real dependencies
│   ├── __init__.py
│   ├── test_database.py
│   └── test_api.py
└── e2e/                  # End-to-end tests
    ├── __init__.py
    └── test_workflows.py
```

### conftest.py (Shared Fixtures)

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Test User"}

@pytest.fixture
def db_session():
    session = create_session()
    yield session
    session.rollback()
    session.close()
```

---

## 6. Config and Secrets

### Environment Variables

```
my-project/
├── .env.example          # Template (committed)
├── .env                  # Local secrets (NOT committed)
└── .env.test             # Test environment
```

**.env.example:**

```bash
DATABASE_URL=postgresql://user:pass@localhost/db
OPENAI_API_KEY=sk-your-key-here
DEBUG=false
```

### Loading Config

```python
# src/my_project/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 7. README.md Template

````markdown
# Project Name

Short description of what this project does.

## Installation

\```bash
uv sync
\```

## Quick Start

\```python
from my_project import main_function

result = main_function()
\```

## Development

\```bash

# Install with dev dependencies

uv sync --dev

# Run tests

uv run pytest

# Run linters

uv run ruff check .
\```

## Configuration

Copy `.env.example` to `.env` and fill in values.

## License

MIT
````

---

## 8. Quick Setup Commands

```bash
# Create new project
uv init my-project
cd my-project

# Create structure
mkdir -p src/my_project tests/unit tests/integration
touch src/my_project/__init__.py
touch tests/__init__.py tests/conftest.py

# Add dev tools
uv add --dev pytest ruff pre-commit

# Setup pre-commit
pre-commit install

# Create config files
touch .env.example .gitignore
```

---

## Quick Reference

### Essential Files

```
pyproject.toml    # Project config
.python-version   # Python version
.gitignore        # Git ignores
.pre-commit-config.yaml
README.md
```

### Standard Directories

```
src/project/      # Source code
tests/            # Test files
.github/          # CI/CD
```

---

## Summary

You've learned:

1. **src layout** — modern project structure
2. **pyproject.toml** — unified configuration
3. **Module organization** — flat → layered → domain
4. **Test structure** — unit, integration, e2e
5. **Config management** — .env files, pydantic settings
6. **README** — documentation template

**Dev Tooling module complete!**

Next: 03-api-patterns — building production APIs.
