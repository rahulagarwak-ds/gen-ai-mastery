# Chapter 3: pytest — Testing Fundamentals

> _"If it's not tested, it's broken."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Writing and organizing tests with pytest
- Fixtures for setup and teardown
- Parametrized tests
- Mocking and patching
- Test coverage
- Best practices for testing

---

## 1. Why pytest?

### unittest (Standard Library)

```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
```

### pytest (Modern)

```python
def test_add():
    assert 1 + 1 == 2
```

**Benefits of pytest:**

- Simple `assert` statements
- Better error messages
- Powerful fixtures
- Huge plugin ecosystem
- Less boilerplate

---

## 2. Installation and Setup

```bash
uv add --dev pytest pytest-cov
```

### Project Structure

```
my-project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── calculator.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Shared fixtures
│   ├── test_calculator.py
│   └── unit/
│       └── test_utils.py
└── pyproject.toml
```

### Configure pytest

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

---

## 3. Writing Tests

### Basic Test

```python
# tests/test_calculator.py
from my_project.calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_divide():
    assert divide(10, 2) == 5.0

def test_divide_by_zero():
    import pytest
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### Testing Classes

```python
class TestCalculator:
    def test_add(self):
        assert add(1, 1) == 2

    def test_subtract(self):
        assert subtract(5, 3) == 2
```

---

## 4. Fixtures

Fixtures provide test data and setup/teardown logic.

### Basic Fixture

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

# tests/test_user.py
def test_user_name(sample_user):
    assert sample_user["name"] == "Alice"

def test_user_email(sample_user):
    assert "@" in sample_user["email"]
```

### Fixture Scopes

```python
@pytest.fixture(scope="function")  # Default: new for each test
def user():
    return create_user()

@pytest.fixture(scope="class")  # Shared within test class
def db_connection():
    return connect_db()

@pytest.fixture(scope="module")  # Shared within test file
def api_client():
    return create_client()

@pytest.fixture(scope="session")  # Shared across all tests
def expensive_resource():
    return load_large_dataset()
```

### Setup and Teardown

```python
@pytest.fixture
def database():
    # Setup
    db = create_database()
    db.connect()

    yield db  # Test runs here

    # Teardown
    db.disconnect()
    db.cleanup()
```

### Fixture Dependencies

```python
@pytest.fixture
def user(database):  # Depends on database fixture
    return database.create_user("Alice")

def test_user(user, database):
    assert database.get_user(user.id) == user
```

---

## 5. Parametrized Tests

Run same test with different inputs.

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Parametrize with IDs

```python
@pytest.mark.parametrize("email,valid", [
    ("user@example.com", True),
    ("invalid", False),
    ("", False),
], ids=["valid_email", "no_at_sign", "empty_string"])
def test_email_validation(email, valid):
    assert validate_email(email) == valid
```

---

## 6. Mocking

### Using unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_api_call():
    # Create mock
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "value"}

    with patch("my_module.requests.get", return_value=mock_response):
        result = fetch_data("http://example.com")

    assert result == {"data": "value"}
```

### Patching

```python
# Patch function
@patch("my_module.external_api")
def test_with_patch(mock_api):
    mock_api.return_value = {"result": "success"}
    result = my_function()
    assert result == {"result": "success"}
    mock_api.assert_called_once()

# Patch class method
@patch.object(MyClass, "method")
def test_method(mock_method):
    mock_method.return_value = 42
    obj = MyClass()
    assert obj.method() == 42
```

### pytest-mock (Recommended)

```bash
uv add --dev pytest-mock
```

```python
def test_with_mocker(mocker):
    mock_api = mocker.patch("my_module.api_call")
    mock_api.return_value = {"status": "ok"}

    result = my_function()

    assert result == {"status": "ok"}
    mock_api.assert_called_once()
```

---

## 7. Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_calculator.py

# Run specific test
pytest tests/test_calculator.py::test_add

# Run tests matching pattern
pytest -k "add"

# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s
```

### Markers

```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.integration
def test_database():
    ...

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    ...

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_specific():
    ...
```

```bash
# Run only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

---

## 8. Test Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html
```

### Configure Coverage

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["*/__init__.py", "*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```

---

## 9. Async Testing

```bash
uv add --dev pytest-asyncio
```

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_fetch_data()
    assert result == expected

@pytest.fixture
async def async_client():
    client = AsyncClient()
    await client.connect()
    yield client
    await client.disconnect()
```

---

## 10. Best Practices

### Naming

```python
# Good: descriptive names
def test_user_creation_with_valid_email_succeeds():
    ...

def test_divide_by_zero_raises_error():
    ...

# Bad: vague names
def test_1():
    ...
```

### Arrange-Act-Assert Pattern

```python
def test_user_can_update_email():
    # Arrange
    user = User(email="old@example.com")

    # Act
    user.update_email("new@example.com")

    # Assert
    assert user.email == "new@example.com"
```

### One Assert Per Test (Guideline)

```python
# Good: focused test
def test_user_email_is_valid():
    user = User(email="test@example.com")
    assert user.email_is_valid()

# Bad: testing multiple things
def test_user():
    user = User(email="test@example.com")
    assert user.email_is_valid()
    assert user.name is None
    assert user.id is not None
```

---

## Quick Reference

### Commands

```bash
pytest                          # Run all
pytest -v                       # Verbose
pytest -x                       # Stop on first fail
pytest -k "pattern"             # Filter by name
pytest -m marker                # Filter by marker
pytest --cov=src                # With coverage
```

### Common Fixtures

```python
@pytest.fixture
def data():
    return setup_data()
    # Automatic teardown with yield

@pytest.fixture(scope="session")
def expensive():
    return load_once()
```

---

## Summary

You've learned:

1. **Writing tests** — assert, pytest.raises
2. **Fixtures** — setup, teardown, scopes
3. **Parametrize** — test multiple inputs
4. **Mocking** — patch external dependencies
5. **Running tests** — commands, markers
6. **Coverage** — measure test completeness

Next chapter: pre-commit — automate quality checks.
