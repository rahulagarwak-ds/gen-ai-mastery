# Mini Project: LLM Client Library

## 🎯 Objective

Build a production-ready LLM client library that abstracts multiple providers, handles errors gracefully, and tracks costs.

---

## 📋 Requirements

### 1. Provider Abstraction

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

class LLMProvider(ABC):
    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        pass

    @abstractmethod
    def stream(
        self,
        messages: list[dict],
        **kwargs
    ) -> Iterator[str]:
        pass
```

### 2. Implement Providers

- `OpenAIProvider` — GPT-4o, GPT-4o-mini
- `AnthropicProvider` — Claude 3.5 Sonnet
- `GoogleProvider` — Gemini 1.5 Pro (optional)

### 3. Features

**Retry Logic:**

```python
# Automatic retry with exponential backoff
# Handle: RateLimitError, APIConnectionError, InternalServerError
```

**Cost Tracking:**

```python
# Track total cost across all calls
client.total_cost  # Returns total USD spent
```

**Token Budgeting:**

```python
# Truncate messages to fit context window
client.chat(messages, max_context_tokens=4000)
```

**Logging:**

```python
# Log all API calls with timing
# [2024-01-01 12:00:00] OpenAI gpt-4o | 150 in, 200 out | 0.3s | $0.0025
```

### 4. Configuration

```python
from pydantic_settings import BaseSettings

class LLMConfig(BaseSettings):
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    default_provider: str = "openai"
    default_model: str = "gpt-4o"
    default_temperature: float = 0.7
    max_retries: int = 3
    timeout: float = 30.0
```

---

## 📁 Project Structure

```
llm_client/
├── __init__.py
├── config.py          # Settings
├── models.py          # LLMResponse, Message
├── providers/
│   ├── __init__.py
│   ├── base.py        # Abstract base
│   ├── openai.py
│   └── anthropic.py
├── client.py          # Main LLMClient class
└── utils.py           # Token counting, cost calc
```

---

## ✅ Test Cases

```python
from llm_client import LLMClient

# Basic usage
client = LLMClient(provider="openai", model="gpt-4o")
response = client.chat([
    {"role": "user", "content": "Hello!"}
])
assert response.content
assert response.cost_usd > 0

# Streaming
for chunk in client.stream([{"role": "user", "content": "Count to 5"}]):
    print(chunk, end="")

# Provider switching
client.set_provider("anthropic", "claude-3-5-sonnet-20241022")
response = client.chat([{"role": "user", "content": "Hello!"}])

# Cost tracking
print(f"Total spent: ${client.total_cost:.4f}")

# With system prompt
response = client.chat(
    messages=[{"role": "user", "content": "Hi"}],
    system="You are a pirate.",
    temperature=0.9
)
```

---

## 🏆 Bonus Challenges

1. Add `AsyncLLMClient` with async/await support
2. Add response caching (same input = cached output)
3. Add fallback providers (if OpenAI fails, try Anthropic)
4. Add usage dashboard (daily/weekly cost reports)

---

## 📁 Deliverable

A complete Python package that can be installed and used:

```bash
uv add ./llm_client
```

```python
from llm_client import LLMClient

client = LLMClient()
response = client.chat([{"role": "user", "content": "Hello!"}])
print(response.content)
```

**Time estimate:** 2-3 hours

---

## 💡 Hints

<details>
<summary>Hint 1: Cost Calculation</summary>

```python
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},  # per 1M tokens
}
cost = (tokens / 1_000_000) * rate
```

</details>

<details>
<summary>Hint 2: Retry with tenacity</summary>

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=60))
def api_call():
    ...
```

</details>
