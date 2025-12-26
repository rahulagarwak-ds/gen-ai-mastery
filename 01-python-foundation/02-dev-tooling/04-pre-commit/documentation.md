# Chapter 4: pre-commit — Automated Quality Checks

> _"Catch issues before they hit the repo."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- What pre-commit hooks are and why they matter
- Setting up pre-commit in your project
- Configuring hooks for Python projects
- Common hooks for code quality
- CI integration

---

## 1. What is pre-commit?

Pre-commit runs checks **before** every git commit:

```
You: git commit -m "Add feature"
    ↓
Pre-commit: Running ruff... ✓
Pre-commit: Running pytest... ✓
Pre-commit: Checking types... ✓
    ↓
Commit succeeds!
```

If any check fails, the commit is blocked until you fix issues.

---

## 2. Installation

```bash
# Install pre-commit
uv add --dev pre-commit

# Or globally
pip install pre-commit
```

---

## 3. Basic Setup

### Create Config File

Create `.pre-commit-config.yaml` in project root:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### Install Hooks

```bash
pre-commit install
```

Now hooks run on every commit!

---

## 4. Full Python Configuration

```yaml
# .pre-commit-config.yaml
repos:
  # Ruff - Linting and Formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # General file checks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: debug-statements

  # Type checking (optional, can be slow)
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
        args: [--ignore-missing-imports]
```

---

## 5. Common Hooks

### Code Quality

```yaml
# Ruff (replaces flake8, isort, black)
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.1.9
  hooks:
    - id: ruff
    - id: ruff-format
```

### Security

```yaml
# Detect secrets
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.4.0
  hooks:
    - id: detect-secrets

# Security linting
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.6
  hooks:
    - id: bandit
      args: ['-c', 'pyproject.toml']
```

### File Hygiene

```yaml
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v4.5.0
  hooks:
    - id: trailing-whitespace # Remove trailing spaces
    - id: end-of-file-fixer # Ensure newline at end
    - id: check-yaml # Validate YAML
    - id: check-json # Validate JSON
    - id: check-toml # Validate TOML
    - id: check-added-large-files # Block large files
    - id: check-merge-conflict # Detect conflict markers
    - id: debug-statements # Detect print/breakpoint
    - id: no-commit-to-branch # Protect main branch
      args: ['--branch', 'main']
```

---

## 6. Running Hooks

### On Commit (Automatic)

```bash
git commit -m "message"
# Hooks run automatically
```

### Run Manually

```bash
# Run all hooks on staged files
pre-commit run

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Skip hooks (emergency only!)
git commit --no-verify -m "hotfix"
```

### Update Hooks

```bash
pre-commit autoupdate
```

---

## 7. Handling Failures

When a hook fails:

```
ruff.....................................................................Failed
- hook id: ruff
- files were modified by this hook

Fixing src/module.py
```

**What to do:**

1. Review the changes made by auto-fixers
2. Stage the fixed files: `git add .`
3. Commit again: `git commit -m "message"`

---

## 8. Skip Specific Hooks

### Skip for One Commit

```bash
SKIP=mypy git commit -m "WIP"
```

### Skip in Config (Per-File)

```yaml
- id: mypy
  exclude: ^tests/
```

---

## 9. CI Integration

### GitHub Actions

```yaml
# .github/workflows/pre-commit.yml
name: pre-commit

on:
  pull_request:
  push:
    branches: [main]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: pre-commit/action@v3.0.0
```

---

## 10. Recommended Setup

### Minimal (Start Here)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### Full Production Setup

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: check-merge-conflict
      - id: debug-statements
      - id: no-commit-to-branch
        args: ['--branch', 'main', '--branch', 'master']

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, types-requests]
        args: [--ignore-missing-imports]
```

---

## Quick Reference

### Setup

```bash
uv add --dev pre-commit
pre-commit install
```

### Commands

```bash
pre-commit run                    # Staged files
pre-commit run --all-files        # All files
pre-commit autoupdate             # Update hooks
git commit --no-verify            # Skip hooks
```

### Config Location

`.pre-commit-config.yaml` in project root

---

## Summary

You've learned:

1. **What pre-commit does** — blocks bad commits
2. **Setup** — config file, install hooks
3. **Common hooks** — ruff, file checks, security
4. **Running** — automatic and manual
5. **CI integration** — GitHub Actions

Next chapter: Project Structure — organizing Python projects.
