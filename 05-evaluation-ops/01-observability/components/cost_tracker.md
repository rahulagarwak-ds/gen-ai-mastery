# Mini Project: LLM Cost Tracker

## 🎯 Objective

Build a cost tracking and monitoring system for LLM API calls.

---

## 📋 Requirements

### 1. Cost Calculator

```python
from dataclasses import dataclass

PRICING = {
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
}

@dataclass
class UsageRecord:
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: str
    user_id: str | None = None

def calculate_cost(record: UsageRecord) -> float:
    """Calculate USD cost for a usage record."""
    pass
```

### 2. Tracker Class

```python
class CostTracker:
    def __init__(self, storage_path: str = "usage.json"):
        pass

    def log(self, record: UsageRecord):
        """Log a usage record."""
        pass

    def get_total_cost(
        self,
        user_id: str = None,
        model: str = None,
        since: str = None
    ) -> float:
        """Get total cost with optional filters."""
        pass

    def get_daily_breakdown(self) -> dict[str, float]:
        """Get cost by date."""
        pass

    def get_model_breakdown(self) -> dict[str, float]:
        """Get cost by model."""
        pass
```

### 3. OpenAI Wrapper

```python
def tracked_chat(tracker: CostTracker, user_id: str = None):
    """Decorator to automatically track costs."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Extract usage and log
            pass
        return wrapper
    return decorator

@tracked_chat(tracker)
def chat(messages: list, model: str = "gpt-4o"):
    pass
```

---

## ✅ Test Cases

```python
tracker = CostTracker("./test_usage.json")

# Log usage
tracker.log(UsageRecord(
    model="gpt-4o",
    input_tokens=1000,
    output_tokens=500,
    timestamp="2024-01-15T10:00:00Z",
    user_id="user_1"
))

# Get costs
total = tracker.get_total_cost()
assert total > 0

by_model = tracker.get_model_breakdown()
assert "gpt-4o" in by_model

by_day = tracker.get_daily_breakdown()
assert "2024-01-15" in by_day
```

**Time estimate:** 2-3 hours
