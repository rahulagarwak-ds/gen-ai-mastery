# Mini Project: Budget Manager

## 🎯 Objective

Build a comprehensive cost tracking and budget management system for LLM APIs.

---

## 📋 Requirements

### 1. Core Types

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class UsageRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    user_id: str | None = None
    endpoint: str | None = None
    request_id: str | None = None

@dataclass
class Budget:
    daily_limit: float = 10.0
    monthly_limit: float = 200.0
    per_request_limit: float = 0.50
    alert_threshold: float = 0.8
```

### 2. Budget Manager

```python
from typing import Callable

class BudgetManager:
    def __init__(
        self,
        budget: Budget,
        alert_handler: Callable[[AlertLevel, str], None] = None
    ):
        pass

    def can_spend(self, estimated_cost: float) -> bool:
        """Check if within budget."""
        pass

    def record_spend(self, record: UsageRecord):
        """Record spending and check alerts."""
        pass

    def get_status(self) -> dict:
        """Get current budget status."""
        return {
            "daily_spent": 0.0,
            "daily_remaining": 0.0,
            "monthly_spent": 0.0,
            "monthly_remaining": 0.0,
            "percent_used": 0.0
        }

    def reset_daily(self):
        """Reset daily counters."""
        pass
```

### 3. Cost Optimizer

```python
class CostOptimizer:
    def __init__(self, pricing: dict[str, dict]):
        self.pricing = pricing

    def select_model(
        self,
        task_type: str,
        max_cost: float = None,
        quality: str = "medium"
    ) -> str:
        """Select optimal model for task."""
        pass

    def estimate_cost(
        self,
        model: str,
        input_text: str,
        expected_output_tokens: int = 500
    ) -> float:
        """Estimate cost before calling."""
        pass

    def recommend_optimizations(
        self,
        usage_records: list[UsageRecord]
    ) -> list[str]:
        """Suggest ways to reduce costs."""
        pass
```

### 4. Tracked Client

```python
class TrackedLLMClient:
    def __init__(
        self,
        budget_manager: BudgetManager,
        optimizer: CostOptimizer
    ):
        pass

    def chat(
        self,
        messages: list[dict],
        model: str = None,
        max_cost: float = None
    ) -> str:
        """Chat with cost tracking and budget check."""
        # 1. Estimate cost
        # 2. Check budget
        # 3. Select optimal model if needed
        # 4. Make call
        # 5. Record actual cost
        pass
```

---

## ✅ Test Cases

```python
# Budget setup
budget = Budget(daily_limit=5.0, monthly_limit=50.0)
manager = BudgetManager(budget, alert_handler=print)
optimizer = CostOptimizer(PRICING)

# Check budget
assert manager.can_spend(0.01) == True
assert manager.can_spend(100.0) == False

# Record spending
manager.record_spend(UsageRecord(
    model="gpt-4o",
    input_tokens=1000,
    output_tokens=500,
    cost_usd=0.05,
    timestamp=datetime.now()
))

# Status check
status = manager.get_status()
assert status["daily_spent"] == 0.05
assert status["daily_remaining"] == 4.95

# Cost optimization
model = optimizer.select_model("summarization", max_cost=0.01)
assert model in ["gpt-4o-mini", "claude-3-haiku"]

# Tracked client
client = TrackedLLMClient(manager, optimizer)
# Should raise if budget exceeded
```

---

## 🎁 Bonus

1. Add cost forecasting based on trends
2. Implement per-user budget tracking
3. Add Slack/email alerts
4. Create cost dashboard visualization
5. Export reports to CSV/Excel

**Time estimate:** 4-5 hours
