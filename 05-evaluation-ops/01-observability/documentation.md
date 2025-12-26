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
