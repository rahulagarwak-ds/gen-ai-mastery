# Chapter 1: uv — The Modern Python Package Manager

> _"pip is dead. Long live uv."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Why uv is replacing pip/poetry/pipenv
- Installing and using uv
- Managing dependencies and virtual environments
- Lock files and reproducible builds
- uv vs other tools comparison

---

## 1. Why uv?

### The Problem with Traditional Tools

| Tool   | Issues                                            |
| ------ | ------------------------------------------------- |
| pip    | No lock files, slow resolution, no env management |
| poetry | Slow, complex, dependency hell                    |
| pipenv | Abandoned, unreliable                             |
| conda  | Heavy, mixing ecosystems                          |

### What uv Offers

- **10-100x faster** than pip/poetry
- **Written in Rust** — lightweight binary
- **Drop-in pip replacement** — same commands
- **Built-in virtual env management**
- **Lock files** for reproducibility
- **Single tool** for everything

---

## 2. Installation

### macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verify

```bash
uv --version
```

---

## 3. Basic Usage

### Create a New Project

```bash
uv init my-project
cd my-project
```

This creates:

```
my-project/
├── .python-version
├── pyproject.toml
├── README.md
└── src/
    └── my_project/
        └── __init__.py
```

### Add Dependencies

```bash
# Add a package
uv add requests

# Add dev dependency
uv add --dev pytest ruff

# Add with version constraint
uv add "pandas>=2.0"
```

### Remove Dependencies

```bash
uv remove requests
```

### Sync Environment

```bash
# Install all dependencies from lock file
uv sync
```

---

## 4. Virtual Environments

### Create and Activate

```bash
# Create venv (automatic with uv init)
uv venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### Run Without Activating

```bash
# Run a command in the venv
uv run python script.py
uv run pytest
uv run ruff check .
```

---

## 5. Lock Files

### Understanding pyproject.toml vs uv.lock

**pyproject.toml** — Your requirements (flexible):

```toml
[project]
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]
```

**uv.lock** — Exact versions (pinned):

```
# Auto-generated, don't edit
requests==2.31.0
pydantic==2.5.2
...
```

### Regenerate Lock File

```bash
uv lock
```

### Why Lock Files Matter

```bash
# Developer A
uv sync  # Gets requests 2.31.0

# Developer B (weeks later)
uv sync  # Also gets requests 2.31.0 (not 2.32.0)
```

Reproducible builds = no "works on my machine" bugs.

---

## 6. Managing Python Versions

### Install Python Versions

```bash
# Install specific Python
uv python install 3.11
uv python install 3.12

# List installed
uv python list
```

### Pin Project Python

```bash
# Create .python-version file
uv python pin 3.11
```

---

## 7. pip Compatibility Mode

uv works as a drop-in pip replacement:

```bash
# Instead of: pip install requests
uv pip install requests

# Instead of: pip install -r requirements.txt
uv pip install -r requirements.txt

# Instead of: pip freeze
uv pip freeze
```

---

## 8. Common Commands Reference

| Task               | Command                  |
| ------------------ | ------------------------ |
| Create project     | `uv init project-name`   |
| Add dependency     | `uv add package`         |
| Add dev dependency | `uv add --dev package`   |
| Remove dependency  | `uv remove package`      |
| Install all deps   | `uv sync`                |
| Update lock file   | `uv lock`                |
| Run command        | `uv run command`         |
| Create venv        | `uv venv`                |
| Install Python     | `uv python install 3.11` |

---

## 9. Migrating from pip/poetry

### From requirements.txt

```bash
uv init my-project
uv add $(cat requirements.txt)
```

### From poetry

```bash
# In existing poetry project
uv init --no-readme
# Edit pyproject.toml to match poetry's dependencies
uv lock
```

---

## 10. Best Practices

### Do:

- ✅ Commit `uv.lock` to git
- ✅ Use `uv run` for scripts
- ✅ Pin Python version with `.python-version`
- ✅ Use `--dev` for test/lint dependencies

### Don't:

- ❌ Edit `uv.lock` manually
- ❌ Mix uv and pip in same project
- ❌ Commit `.venv/` directory

---

## Quick Reference

```bash
# Start new project
uv init my-app && cd my-app

# Add dependencies
uv add fastapi uvicorn
uv add --dev pytest ruff

# Run
uv run python -m my_app
uv run pytest
```

---

## Summary

You've learned:

1. **Why uv** — fast, modern, all-in-one
2. **Project creation** — `uv init`
3. **Dependencies** — `uv add/remove`
4. **Lock files** — reproducible builds
5. **Python management** — multiple versions
6. **Best practices** — commit locks, use `uv run`

Next chapter: ruff — the lightning-fast linter and formatter.
