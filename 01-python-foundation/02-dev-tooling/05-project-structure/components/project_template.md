# Mini Project: Python Project Template

## 🎯 Objective

Create a reusable Python project template with all modern tooling configured. This template will be the foundation for all your future projects.

---

## 📋 Requirements

### 1. Project Structure

Create the following structure:

```
python-template/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── pyproject.toml
└── README.md
```

### 2. pyproject.toml

Include:

- Project metadata (name, version, description)
- Python >= 3.11
- Build system (hatchling)
- Dependencies: none for template
- Dev dependencies: pytest, pytest-cov, ruff, pre-commit
- ruff configuration
- pytest configuration

### 3. .pre-commit-config.yaml

Include at minimum:

- ruff (check + format)
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- check-added-large-files

### 4. GitHub Actions CI

Create `.github/workflows/ci.yml` that:

- Runs on push and PR
- Uses Python 3.11
- Installs dependencies with uv
- Runs ruff check
- Runs pytest with coverage
- Fails if coverage < 80%

### 5. Sample Code

**src/my_project/main.py:**

```python
def greet(name: str) -> str:
    """Return a greeting message."""
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"

def main() -> None:
    print(greet("World"))

if __name__ == "__main__":
    main()
```

**tests/test_main.py:**

```python
import pytest
from my_project.main import greet

def test_greet():
    assert greet("Alice") == "Hello, Alice!"

def test_greet_empty_raises():
    with pytest.raises(ValueError):
        greet("")
```

### 6. README.md

Include:

- Project description
- Installation instructions
- Usage example
- Development setup
- Testing instructions

---

## ✅ Verification

Your template should pass these checks:

```bash
# Install dependencies
uv sync

# Linting passes
uv run ruff check .

# Formatting passes
uv run ruff format --check .

# Tests pass with 100% coverage
uv run pytest --cov=src --cov-fail-under=100

# Pre-commit passes
pre-commit run --all-files
```

---

## 🏆 Bonus Challenges

1. Add mypy type checking to CI
2. Add Docker support (Dockerfile + docker-compose.yml)
3. Add Makefile with common commands
4. Create a cookiecutter template from your project

---

## 📁 Deliverable

A complete project template that you can use with:

```bash
# Copy template
cp -r python-template my-new-project
cd my-new-project

# Rename package
mv src/my_project src/actual_project_name

# Initialize
uv sync
pre-commit install
```

**Time estimate:** 45-60 minutes
