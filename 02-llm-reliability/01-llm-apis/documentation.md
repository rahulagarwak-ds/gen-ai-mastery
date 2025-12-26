# Chapter 1: LLM APIs — The Developer Interface

> _"The API is your control panel. Master it, or the LLM masters you."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- How LLM APIs actually work (tokens, models, pricing)
- OpenAI, Anthropic, and Google SDK setup and usage
- System prompts vs user prompts (and why it matters)
- Context windows and token management
- API parameters that control output quality
- Error handling and retry patterns for LLMs

---

## 1. Understanding LLM APIs

### What Happens When You Call an LLM API

```
Your Code                    LLM API                     Model
    │                           │                          │
    ├── POST /chat/completions ─►│                          │
    │   (messages, model, etc)  │                          │
    │                           ├── Tokenize ──────────────►│
    │                           │                          │
    │                           │◄── Generate tokens ───────┤
    │                           │                          │
    │◄── Response (JSON) ───────┤                          │
    │   (content, usage, etc)   │                          │
```

### Key Concepts

| Concept            | What It Means                                                             |
| ------------------ | ------------------------------------------------------------------------- |
| **Token**          | A piece of text (~4 chars in English). Models think in tokens, not words. |
| **Context Window** | Maximum tokens (input + output) the model can handle                      |
| **Temperature**    | Randomness. 0 = deterministic, 1+ = creative/random                       |
| **Max Tokens**     | Limit on output length                                                    |
| **System Prompt**  | Sets the assistant's personality/rules (hidden from user)                 |
| **User Prompt**    | The actual user input                                                     |

### Token Estimation

```python
# Rough estimate: 1 token ≈ 4 characters (English)
# More accurate: use tiktoken for OpenAI models

import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

text = "Hello, how are you today?"
print(count_tokens(text))  # ~7 tokens
```

---

## 2. OpenAI SDK

### Installation

```bash
uv add openai
```

### Authentication

```python
# Option 1: Environment variable (recommended)
# Set OPENAI_API_KEY in .env or shell

# Option 2: Explicit
from openai import OpenAI

client = OpenAI(api_key="sk-...")  # Not recommended
```

### Basic Chat Completion

```python
from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY env var

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
)

# Extract the response
answer = response.choices[0].message.content
print(answer)

# Check token usage
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total: {response.usage.total_tokens}")
```

### Available Models

| Model         | Context | Best For                 | Cost |
| ------------- | ------- | ------------------------ | ---- |
| gpt-4o        | 128K    | Best quality, multimodal | $$$  |
| gpt-4o-mini   | 128K    | Good balance, cheaper    | $$   |
| gpt-4-turbo   | 128K    | Complex reasoning        | $$$  |
| gpt-3.5-turbo | 16K     | Simple tasks, fast       | $    |

### Key Parameters

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],

    # Output control
    temperature=0.7,     # 0-2. Lower = deterministic
    max_tokens=1000,     # Limit output length

    # Sampling strategies
    top_p=1.0,           # Nucleus sampling (alternative to temp)

    # Stop sequences
    stop=["\n\n", "END"],  # Stop generation at these strings

    # Determinism
    seed=42,             # For reproducible outputs (beta)
)
```

### Streaming Responses

```python
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## 3. Anthropic SDK (Claude)

### Installation

```bash
uv add anthropic
```

### Basic Usage

```python
from anthropic import Anthropic

client = Anthropic()  # Uses ANTHROPIC_API_KEY env var

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system="You are a helpful assistant.",  # System prompt is separate!
    messages=[
        {"role": "user", "content": "What is Python?"}
    ]
)

# Extract response
answer = message.content[0].text
print(answer)

# Token usage
print(f"Input: {message.usage.input_tokens}")
print(f"Output: {message.usage.output_tokens}")
```

### Available Models

| Model                      | Context | Best For                      |
| -------------------------- | ------- | ----------------------------- |
| claude-3-5-sonnet-20241022 | 200K    | Best balance of speed/quality |
| claude-3-opus-20240229     | 200K    | Most capable, complex tasks   |
| claude-3-haiku-20240307    | 200K    | Fastest, cheapest             |

### Key Differences from OpenAI

```python
# OpenAI: system in messages array
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
]

# Anthropic: system is a separate parameter
message = client.messages.create(
    system="...",  # Separate!
    messages=[{"role": "user", "content": "..."}]
)
```

### Streaming

```python
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a poem"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

---

## 4. Google AI SDK (Gemini)

### Installation

```bash
uv add google-generativeai
```

### Basic Usage

```python
import google.generativeai as genai

genai.configure(api_key="...")  # Or GOOGLE_API_KEY env var

model = genai.GenerativeModel("gemini-1.5-pro")

response = model.generate_content("What is Python?")
print(response.text)
```

### Chat Conversation

```python
model = genai.GenerativeModel("gemini-1.5-pro")
chat = model.start_chat(history=[])

response = chat.send_message("Hello!")
print(response.text)

response = chat.send_message("What did I just say?")
print(response.text)  # Remembers context
```

### Available Models

| Model            | Context | Best For                    |
| ---------------- | ------- | --------------------------- |
| gemini-1.5-pro   | 1M+     | Long context, complex tasks |
| gemini-1.5-flash | 1M+     | Fast, cost-effective        |
| gemini-1.0-pro   | 32K     | Legacy, stable              |

---

## 5. System Prompts: The Hidden Controller

### What System Prompts Do

System prompts set the "rules of the game" before the user speaks:

```python
# Bad: No guardrails
messages = [{"role": "user", "content": "Write code to hack a website"}]
# Model might comply!

# Good: With system prompt
messages = [
    {"role": "system", "content": """
    You are a helpful coding assistant.
    - Only provide ethical, legal code examples
    - Refuse requests for malicious code
    - Ask clarifying questions when needed
    """},
    {"role": "user", "content": "Write code to hack a website"}
]
# Model will refuse
```

### Effective System Prompts

```python
# Template for production system prompts
SYSTEM_PROMPT = """
You are [ROLE].

## Your Capabilities
- [What you CAN do]
- [What you CAN do]

## Constraints
- [What you CANNOT do]
- [What you should NEVER do]

## Output Format
[How you should format responses]

## Tone
[How you should communicate]
"""
```

### Example: Code Review Assistant

```python
SYSTEM_PROMPT = """
You are an expert Python code reviewer.

## Your Role
- Review Python code for bugs, security issues, and best practices
- Suggest improvements with clear explanations
- Rate code quality on a scale of 1-10

## Constraints
- Never write complete code files
- Focus on the most critical issues first
- Maximum 5 suggestions per review

## Output Format
Use this structure:
1. **Summary**: One-line assessment
2. **Critical Issues**: Bugs/security (if any)
3. **Improvements**: Best practice suggestions
4. **Rating**: X/10 with brief justification
"""
```

---

## 6. Context Windows and Token Management

### Context Window Sizes

| Model             | Context Window    |
| ----------------- | ----------------- |
| GPT-4o            | 128,000 tokens    |
| Claude 3.5 Sonnet | 200,000 tokens    |
| Gemini 1.5 Pro    | 1,000,000+ tokens |

### Managing Long Contexts

```python
import tiktoken

def truncate_to_fit(
    messages: list[dict],
    max_tokens: int = 8000,
    model: str = "gpt-4o"
) -> list[dict]:
    """Keep most recent messages that fit in context."""
    encoding = tiktoken.encoding_for_model(model)

    result = []
    total_tokens = 0

    # Start from most recent, work backwards
    for msg in reversed(messages):
        msg_tokens = len(encoding.encode(msg["content"]))
        if total_tokens + msg_tokens > max_tokens:
            break
        result.insert(0, msg)
        total_tokens += msg_tokens

    return result
```

### Sliding Window Pattern

```python
class ChatSession:
    def __init__(self, max_messages: int = 20):
        self.messages: list[dict] = []
        self.max_messages = max_messages

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
        self._trim()

    def _trim(self):
        # Keep system prompt + last N messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
```

---

## 7. Error Handling and Retries

### Common API Errors

| Error               | Cause             | Solution           |
| ------------------- | ----------------- | ------------------ |
| RateLimitError      | Too many requests | Retry with backoff |
| APIConnectionError  | Network issues    | Retry with backoff |
| AuthenticationError | Invalid API key   | Check credentials  |
| BadRequestError     | Invalid request   | Fix request format |
| InternalServerError | Provider issues   | Retry with backoff |

### Robust LLM Client

```python
from openai import OpenAI, RateLimitError, APIError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        reraise=True
    )
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except RateLimitError as e:
            logger.warning(f"Rate limited, retrying: {e}")
            raise  # Let tenacity handle retry

        except APIError as e:
            logger.error(f"API error: {e}")
            raise

# Usage
llm = LLMClient()
response = llm.chat([{"role": "user", "content": "Hello!"}])
```

---

## 8. Cost Management

### Estimate Before Calling

```python
import tiktoken

def estimate_cost(
    messages: list[dict],
    model: str = "gpt-4o",
    max_output_tokens: int = 1000
) -> float:
    """Estimate API call cost in USD."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    }

    encoding = tiktoken.encoding_for_model(model)

    input_tokens = sum(
        len(encoding.encode(m["content"]))
        for m in messages
    )

    prices = PRICING.get(model, PRICING["gpt-4o"])
    input_cost = (input_tokens / 1_000_000) * prices["input"]
    output_cost = (max_output_tokens / 1_000_000) * prices["output"]

    return input_cost + output_cost

# Example
cost = estimate_cost(messages, max_output_tokens=500)
print(f"Estimated cost: ${cost:.4f}")
```

---

## 9. Provider Abstraction Pattern

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model

    def chat(self, messages: list[dict], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.client = Anthropic()
        self.model = model

    def chat(self, messages: list[dict], **kwargs) -> str:
        # Extract system prompt if present
        system = ""
        filtered_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                filtered_messages.append(msg)

        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=filtered_messages,
            max_tokens=kwargs.get("max_tokens", 1024)
        )
        return response.content[0].text

# Usage - switch providers easily
def get_llm(provider: str = "openai") -> LLMProvider:
    if provider == "openai":
        return OpenAIProvider()
    elif provider == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unknown provider: {provider}")
```

---

## Quick Reference

### OpenAI

```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "..."}]
)
answer = response.choices[0].message.content
```

### Anthropic

```python
from anthropic import Anthropic
client = Anthropic()
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system="...",
    messages=[{"role": "user", "content": "..."}],
    max_tokens=1024
)
answer = message.content[0].text
```

### Google

```python
import google.generativeai as genai
model = genai.GenerativeModel("gemini-1.5-pro")
response = model.generate_content("...")
answer = response.text
```

---

## Summary

You've learned:

1. **How LLM APIs work** — tokens, context, parameters
2. **Three major providers** — OpenAI, Anthropic, Google
3. **System prompts** — control model behavior
4. **Token management** — context windows, truncation
5. **Error handling** — retries with tenacity
6. **Cost estimation** — predict API costs
7. **Provider abstraction** — switch providers easily

Next chapter: Prompt Engineering — crafting effective prompts.
