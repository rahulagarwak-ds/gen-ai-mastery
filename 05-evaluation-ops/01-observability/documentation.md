# Chapter 1: Observability — Seeing Inside Your AI System

> _"You can't fix what you can't see."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Why LLM observability matters
- Logging LLM calls with context
- Distributed tracing for AI pipelines
- Key metrics to track
- Popular observability tools (LangSmith, Langfuse)

---

## 1. Why Observability?

### The Challenge

LLM applications are non-deterministic:

- Same input can produce different outputs
- Failures are often semantic, not technical
- Debugging requires context (prompts, responses, latency)

### What to Track

| Category        | Examples                          |
| --------------- | --------------------------------- |
| **Inputs**      | Prompts, system messages, context |
| **Outputs**     | Responses, tokens, tool calls     |
| **Performance** | Latency, token counts, cost       |
| **Quality**     | Errors, feedback, scores          |

---

## 2. Structured Logging

### Basic LLM Logger

```python
import json
import logging
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm")

@dataclass
class LLMLog:
    timestamp: str
    model: str
    prompt: str
    response: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    metadata: dict = None

def log_llm_call(log: LLMLog):
    logger.info(json.dumps(asdict(log)))
```

### Usage with OpenAI

```python
import time
from openai import OpenAI

client = OpenAI()

def chat(messages: list[dict], model: str = "gpt-4o-mini") -> str:
    start = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    latency = (time.time() - start) * 1000
    usage = response.usage

    log_llm_call(LLMLog(
        timestamp=datetime.utcnow().isoformat(),
        model=model,
        prompt=str(messages),
        response=response.choices[0].message.content,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        latency_ms=latency,
        cost_usd=calculate_cost(model, usage),
        metadata={"request_id": response.id}
    ))

    return response.choices[0].message.content
```

---

## 3. Tracing with Context

### Trace Structure

```
Trace: "user_query_123"
├── Span: embed_query (50ms)
├── Span: vector_search (120ms)
├── Span: llm_call (850ms)
│   └── metadata: {model, tokens, cost}
└── Span: format_response (10ms)
```

### Simple Tracer

```python
import uuid
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: float = field(default_factory=time.time)
    end_time: float = None
    metadata: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

class Tracer:
    def __init__(self):
        self.traces = {}
        self._current_trace = None
        self._current_span = None

    @contextmanager
    def trace(self, name: str):
        trace_id = str(uuid.uuid4())[:8]
        self._current_trace = trace_id
        root_span = Span(name=name, trace_id=trace_id)
        self._current_span = root_span
        self.traces[trace_id] = root_span

        try:
            yield trace_id
        finally:
            root_span.end_time = time.time()
            self._log_trace(root_span)

    @contextmanager
    def span(self, name: str, **metadata):
        parent = self._current_span
        child = Span(
            name=name,
            trace_id=self._current_trace,
            metadata=metadata
        )
        parent.children.append(child)
        self._current_span = child

        try:
            yield child
        finally:
            child.end_time = time.time()
            self._current_span = parent

    def _log_trace(self, span: Span):
        duration = (span.end_time - span.start_time) * 1000
        print(f"[{span.trace_id}] {span.name}: {duration:.0f}ms")
        for child in span.children:
            self._log_trace(child)

tracer = Tracer()
```

### Usage

```python
with tracer.trace("rag_query"):
    with tracer.span("embed"):
        embedding = embed(query)

    with tracer.span("search"):
        docs = vector_store.search(embedding)

    with tracer.span("generate", model="gpt-4o"):
        response = generate(query, docs)
```

---

## 4. LangSmith Integration

### Setup

```bash
uv add langsmith
export LANGCHAIN_API_KEY="your-key"
export LANGCHAIN_TRACING_V2="true"
```

### Automatic Tracing

```python
from langsmith import traceable

@traceable(name="generate_answer")
def generate_answer(query: str, context: list[str]) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Answer based on context."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )
    return response.choices[0].message.content
```

### Manual Runs

```python
from langsmith import Client

client = Client()

# Log a run
client.create_run(
    name="llm_call",
    run_type="llm",
    inputs={"prompt": "..."},
    outputs={"response": "..."},
    start_time=datetime.now(),
    end_time=datetime.now(),
)
```

---

## 5. Langfuse (Open Source)

### Setup

```bash
uv add langfuse
```

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk-...",
    secret_key="sk-...",
    host="https://cloud.langfuse.com"
)
```

### Tracing

```python
from langfuse.decorators import observe

@observe()
def rag_pipeline(query: str) -> str:
    docs = retrieve(query)
    return generate(query, docs)

@observe(as_type="generation")
def generate(query: str, docs: list) -> str:
    response = client.chat.completions.create(...)
    return response.choices[0].message.content
```

### Manual Traces

```python
trace = langfuse.trace(name="rag_query", user_id="user123")

generation = trace.generation(
    name="llm_call",
    model="gpt-4o",
    input=messages,
    output=response,
    usage={"input": 100, "output": 50}
)
```

---

## 6. Key Metrics

### Performance Metrics

```python
from dataclasses import dataclass
from statistics import mean, median

@dataclass
class LLMMetrics:
    latency_p50: float
    latency_p95: float
    tokens_per_second: float
    error_rate: float
    cost_per_query: float

def calculate_metrics(logs: list[LLMLog]) -> LLMMetrics:
    latencies = sorted([l.latency_ms for l in logs])
    total_tokens = sum(l.output_tokens for l in logs)
    total_time = sum(l.latency_ms for l in logs) / 1000
    errors = sum(1 for l in logs if l.metadata.get("error"))

    return LLMMetrics(
        latency_p50=latencies[len(latencies)//2],
        latency_p95=latencies[int(len(latencies)*0.95)],
        tokens_per_second=total_tokens / total_time if total_time > 0 else 0,
        error_rate=errors / len(logs) if logs else 0,
        cost_per_query=mean([l.cost_usd for l in logs])
    )
```

### Dashboard Metrics

| Metric           | Description          | Target |
| ---------------- | -------------------- | ------ |
| Latency P50      | Median response time | <1s    |
| Latency P95      | 95th percentile      | <3s    |
| Error rate       | Failed requests      | <1%    |
| Token efficiency | Output/input ratio   | Varies |
| Cost per query   | USD per request      | Budget |

---

## 7. Production Patterns

### Request ID Propagation

```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### Async Logging

```python
import asyncio
from collections import deque

class AsyncLogger:
    def __init__(self, batch_size: int = 100):
        self.buffer = deque()
        self.batch_size = batch_size

    def log(self, entry: dict):
        self.buffer.append(entry)
        if len(self.buffer) >= self.batch_size:
            asyncio.create_task(self._flush())

    async def _flush(self):
        batch = [self.buffer.popleft() for _ in range(min(len(self.buffer), self.batch_size))]
        # Send to logging service
        await send_to_backend(batch)
```

---

## 8. Cost Management

### Token Pricing (per 1M tokens)

```python
PRICING = {
    # OpenAI
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},

    # Anthropic
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},

    # Google
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD."""
    prices = PRICING.get(model, {"input": 0, "output": 0})
    return (
        (input_tokens / 1_000_000) * prices["input"] +
        (output_tokens / 1_000_000) * prices["output"]
    )
```

### Budget Manager

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

@dataclass
class Budget:
    daily_limit: float = 10.0    # USD per day
    monthly_limit: float = 200.0  # USD per month
    alert_threshold: float = 0.8  # Alert at 80%

@dataclass
class BudgetManager:
    budget: Budget = field(default_factory=Budget)
    on_alert: Callable[[str], None] = None
    _daily_spend: float = 0.0
    _monthly_spend: float = 0.0
    _last_reset: datetime = field(default_factory=datetime.now)

    def track(self, cost: float):
        """Track spending and check limits."""
        self._reset_if_needed()
        self._daily_spend += cost
        self._monthly_spend += cost

        # Check alerts
        if self._daily_spend >= self.budget.daily_limit * self.budget.alert_threshold:
            self._alert(f"Daily budget {self._daily_spend / self.budget.daily_limit:.0%} used")

        if self._monthly_spend >= self.budget.monthly_limit * self.budget.alert_threshold:
            self._alert(f"Monthly budget {self._monthly_spend / self.budget.monthly_limit:.0%} used")

    def can_spend(self, estimated_cost: float) -> bool:
        """Check if spending is within limits."""
        return (
            self._daily_spend + estimated_cost <= self.budget.daily_limit and
            self._monthly_spend + estimated_cost <= self.budget.monthly_limit
        )

    def get_remaining(self) -> dict:
        """Get remaining budget."""
        return {
            "daily": self.budget.daily_limit - self._daily_spend,
            "monthly": self.budget.monthly_limit - self._monthly_spend
        }

    def _alert(self, message: str):
        if self.on_alert:
            self.on_alert(message)

    def _reset_if_needed(self):
        now = datetime.now()
        if now.date() > self._last_reset.date():
            self._daily_spend = 0
        if now.month > self._last_reset.month:
            self._monthly_spend = 0
        self._last_reset = now
```

### Cost Optimization Strategies

#### 1. Model Selection by Task

```python
def select_model(task_type: str, quality_required: str) -> str:
    """Select optimal model for task and quality."""

    MODEL_MAP = {
        # Simple tasks - use cheap models
        ("classification", "low"): "gpt-4o-mini",
        ("summarization", "low"): "gpt-4o-mini",
        ("extraction", "low"): "gpt-4o-mini",

        # Medium complexity
        ("generation", "medium"): "gpt-4o-mini",
        ("analysis", "medium"): "claude-3-haiku",

        # High quality required
        ("reasoning", "high"): "gpt-4o",
        ("code", "high"): "claude-3-5-sonnet",
        ("complex", "high"): "gpt-4o",
    }

    return MODEL_MAP.get((task_type, quality_required), "gpt-4o-mini")
```

#### 2. Prompt Optimization

```python
def optimize_prompt(prompt: str, max_tokens: int = 1000) -> str:
    """Reduce prompt tokens while preserving meaning."""

    # Remove excessive whitespace
    prompt = " ".join(prompt.split())

    # Truncate if needed
    words = prompt.split()
    if len(words) > max_tokens:
        prompt = " ".join(words[:max_tokens]) + "..."

    return prompt

def estimate_tokens(text: str) -> int:
    """Rough token estimate (4 chars ≈ 1 token)."""
    return len(text) // 4
```

#### 3. Caching for Cost Reduction

```python
import hashlib

class CostAwareCache:
    def __init__(self, budget_manager: BudgetManager):
        self.cache = {}
        self.budget = budget_manager
        self.cache_hits = 0
        self.cache_misses = 0

    def get_or_call(self, key: str, fn: Callable, estimated_cost: float):
        """Cache result to avoid repeated API calls."""
        cache_key = hashlib.md5(key.encode()).hexdigest()

        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]

        # Check budget before calling
        if not self.budget.can_spend(estimated_cost):
            raise Exception(f"Budget exceeded. Remaining: {self.budget.get_remaining()}")

        result = fn()
        self.cache[cache_key] = result
        self.cache_misses += 1
        return result

    def savings_report(self) -> dict:
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses + 1e-8)
        }
```

#### 4. Batching Requests

```python
async def batch_embeddings(
    texts: list[str],
    batch_size: int = 100
) -> list[list[float]]:
    """Batch embedding calls to reduce overhead."""
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=batch
        )
        embeddings.extend([e.embedding for e in response.data])

    return embeddings
```

### Cost Monitoring Dashboard

```python
@dataclass
class CostReport:
    period: str
    total_cost: float
    by_model: dict[str, float]
    by_endpoint: dict[str, float]
    daily_trend: list[float]
    top_expensive_calls: list[dict]

def generate_cost_report(logs: list[LLMLog], period_days: int = 30) -> CostReport:
    """Generate cost analytics report."""

    by_model = {}
    by_endpoint = {}
    daily = {}

    for log in logs:
        # By model
        by_model[log.model] = by_model.get(log.model, 0) + log.cost_usd

        # By endpoint
        endpoint = log.metadata.get("endpoint", "unknown")
        by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + log.cost_usd

        # Daily
        day = log.timestamp[:10]
        daily[day] = daily.get(day, 0) + log.cost_usd

    # Top expensive
    sorted_logs = sorted(logs, key=lambda x: x.cost_usd, reverse=True)

    return CostReport(
        period=f"{period_days} days",
        total_cost=sum(l.cost_usd for l in logs),
        by_model=by_model,
        by_endpoint=by_endpoint,
        daily_trend=list(daily.values()),
        top_expensive_calls=[
            {"model": l.model, "cost": l.cost_usd, "tokens": l.input_tokens + l.output_tokens}
            for l in sorted_logs[:10]
        ]
    )
```

---

## Quick Reference

### Structured Log

```python
log_llm_call(LLMLog(model=..., prompt=..., response=..., latency_ms=...))
```

### LangSmith

```python
@traceable(name="my_function")
def my_function(): ...
```

### Langfuse

```python
@observe()
def my_function(): ...
```

---

## Summary

You've learned:

1. **Why observe** — Debug non-deterministic systems
2. **Structured logging** — Capture LLM call details
3. **Tracing** — Connect related operations
4. **LangSmith** — Managed observability
5. **Langfuse** — Open-source alternative
6. **Metrics** — Latency, errors, cost

Next chapter: Evaluation — Measuring AI quality.
