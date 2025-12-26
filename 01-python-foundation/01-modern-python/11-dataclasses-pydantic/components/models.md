# Mini Project: Pydantic Models for Gen AI

## 🎯 Objective

Build a collection of Pydantic models that you'll reuse across Gen AI applications: LLM chat, structured outputs, RAG pipelines, and API responses.

---

## 📋 Part 1: API Response Models

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """
    Generic API response wrapper.

    Features:
        - success: bool
        - data: T | None
        - error: str | None
        - error_code: str | None
        - timestamp: datetime (auto-set)

    Class methods:
        - ok(data: T) -> Create success response
        - fail(error: str, code: str) -> Create error response
    """
    pass

class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated list response.

    Fields:
        - items: list[T]
        - total: int
        - page: int
        - page_size: int
        - has_next: bool
        - has_prev: bool
    """
    pass
```

---

## 📋 Part 2: LLM Chat Models

```python
class Message(BaseModel):
    """
    Single chat message.

    Fields:
        - role: Literal["system", "user", "assistant"]
        - content: str
    """
    pass

class ChatRequest(BaseModel):
    """
    Request to LLM API.

    Fields:
        - messages: list[Message]
        - model: str = "gpt-4"
        - temperature: float (0-2, default 0.7)
        - max_tokens: int | None
        - stream: bool = False
    """
    pass

class Usage(BaseModel):
    """Token usage: prompt_tokens, completion_tokens, total_tokens"""
    pass

class ChatResponse(BaseModel):
    """
    Response from LLM.

    Fields:
        - content: str
        - model: str
        - usage: Usage
        - finish_reason: Literal["stop", "length", "content_filter"] | None
    """
    pass
```

---

## 📋 Part 3: Structured Output Models

```python
class ExtractedEntity(BaseModel):
    """
    Entity extracted from text.

    Fields:
        - name: str
        - entity_type: str
        - confidence: float (0-1)
        - start_char: int | None
        - end_char: int | None
    """
    pass

class Sentiment(BaseModel):
    """
    Sentiment analysis result.

    Fields:
        - label: Literal["positive", "negative", "neutral"]
        - score: float (0-1)
        - explanation: str | None
    """
    pass

class Classification(BaseModel):
    """
    Text classification result.

    Fields:
        - category: str
        - confidence: float (0-1)
        - subcategories: list[str] = []
    """
    pass

class Summary(BaseModel):
    """
    Summarization result.

    Fields:
        - summary: str
        - key_points: list[str]
        - word_count: int
    """
    pass
```

---

## 📋 Part 4: RAG Models

```python
class Document(BaseModel):
    """
    Document chunk for RAG.

    Fields:
        - id: str
        - content: str
        - metadata: dict = {}
        - embedding: list[float] | None
    """
    pass

class SearchResult(BaseModel):
    """
    Vector search result.

    Fields:
        - document: Document
        - score: float
        - rank: int
    """
    pass

class RAGQuery(BaseModel):
    """
    RAG query request.

    Fields:
        - query: str
        - k: int (1-20, default 5)
        - filter: dict | None
        - rerank: bool = False
    """
    pass

class RAGResponse(BaseModel):
    """
    RAG response with sources.

    Fields:
        - answer: str
        - sources: list[SearchResult]
        - query: str
        - model: str
    """
    pass
```

---

## 📋 Part 5: Configuration Models

```python
from pydantic import SecretStr

class LLMConfig(BaseModel):
    """
    LLM provider config.

    Fields:
        - provider: Literal["openai", "anthropic", "google"]
        - model: str
        - api_key: SecretStr (masked in output)
        - temperature: float = 0.7
        - max_tokens: int = 4096
        - timeout: float = 30.0
    """
    pass
```

---

## ✅ Test Cases

```python
# API Response
response = APIResponse[dict].ok({"user_id": 123})
assert response.success == True
assert response.data == {"user_id": 123}

# Chat
request = ChatRequest(
    messages=[
        Message(role="user", content="Hello!")
    ],
    temperature=0.5
)
assert request.model == "gpt-4"

# Serialization
print(request.model_dump_json())

# Validation
try:
    ChatRequest(messages=[], temperature=5.0)  # Should fail
except Exception:
    print("Validation caught invalid temperature")

# Config with secret
config = LLMConfig(
    provider="openai",
    model="gpt-4",
    api_key="sk-secret123"
)
print(config.model_dump())  # api_key should be masked
```

---

## 🏆 Bonus Challenges

1. Add `model_config` with `json_schema_extra` for OpenAI function calling
2. Add `FunctionCall` and `ToolUse` models for agent workflows
3. Add validators that check `content` is not empty for Message

---

## 📁 Deliverable

Create `models.py` with all Pydantic models.

**Time estimate:** 60-90 minutes

---

## 💡 Hints

<details>
<summary>Hint 1: Generic Response</summary>

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T | None = None
```

</details>

<details>
<summary>Hint 2: SecretStr</summary>

`SecretStr` automatically masks the value when serialized.

</details>
