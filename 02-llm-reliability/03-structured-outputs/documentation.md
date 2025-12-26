# Chapter 3: Structured Outputs — Reliable Data from LLMs

> _"If you can't parse it, you can't use it."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Why structured outputs matter for production systems
- JSON mode in OpenAI and Anthropic
- Pydantic validation for LLM responses
- Function calling / tool use for structured data
- The Instructor library for bulletproof extraction
- Retry strategies for malformed outputs

---

## 1. The Problem: Unstructured Chaos

### What Can Go Wrong

```python
# You ask for JSON...
prompt = "Return the user's name and age as JSON"

# LLM returns...
response_1 = '{"name": "Alice", "age": 30}'        # ✓ Perfect
response_2 = 'Here is the JSON: {"name": "Bob"}'   # ✗ Extra text
response_3 = "{'name': 'Carol', 'age': 25}"        # ✗ Single quotes
response_4 = '{"name": "Dave", "age": "thirty"}'   # ✗ Wrong type
response_5 = 'I cannot provide personal info'      # ✗ Refused
```

### The Solution: Multiple Layers

```
                    ┌─────────────────────┐
                    │  1. JSON Mode       │  ← Guarantees valid JSON
                    └─────────────────────┘
                             ↓
                    ┌─────────────────────┐
                    │  2. Pydantic        │  ← Validates structure
                    └─────────────────────┘
                             ↓
                    ┌─────────────────────┐
                    │  3. Retry Logic     │  ← Handles failures
                    └─────────────────────┘
```

---

## 2. OpenAI JSON Mode

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},  # ← Force JSON
    messages=[
        {"role": "system", "content": "Return JSON with name and age fields."},
        {"role": "user", "content": "Extract: Alice is 30 years old."}
    ]
)

import json
data = json.loads(response.choices[0].message.content)
print(data)  # {"name": "Alice", "age": 30}
```

### ⚠️ Important Rules

1. **Must mention JSON in prompt** — OpenAI requires "JSON" somewhere in messages
2. **Only guarantees valid JSON** — Not the schema you want
3. **May still return unexpected structure**

```python
# ❌ This will error
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[
        {"role": "user", "content": "Tell me about Python"}  # No JSON mentioned!
    ]
)

# ✓ This works
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": "Always respond in JSON format."},
        {"role": "user", "content": "Tell me about Python"}
    ]
)
```

---

## 3. OpenAI Structured Outputs (Beta)

### Define Schema with Pydantic

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class UserInfo(BaseModel):
    name: str
    age: int
    email: str | None = None

response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",  # Specific model required
    messages=[
        {"role": "user", "content": "Alice is 30, email alice@example.com"}
    ],
    response_format=UserInfo  # ← Pydantic model
)

user = response.choices[0].message.parsed
print(user.name)   # Alice
print(user.age)    # 30
print(user.email)  # alice@example.com
```

### Complex Nested Structures

```python
from pydantic import BaseModel, Field
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str = Field(description="Task title")
    priority: Priority
    subtasks: list[str] = Field(default_factory=list)

class ProjectPlan(BaseModel):
    project_name: str
    deadline: str
    tasks: list[Task]

response = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "user", "content": """
        Create a project plan for launching a mobile app.
        Include 3 tasks with priorities and subtasks.
        """}
    ],
    response_format=ProjectPlan
)

plan = response.choices[0].message.parsed
for task in plan.tasks:
    print(f"{task.priority.value}: {task.title}")
```

---

## 4. Anthropic Tool Use for Structure

Anthropic uses "tools" to get structured outputs:

```python
from anthropic import Anthropic

client = Anthropic()

# Define the structure as a tool
tools = [
    {
        "name": "extract_user",
        "description": "Extract user information from text",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["name", "age"]
        }
    }
]

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "tool", "name": "extract_user"},  # Force this tool
    messages=[
        {"role": "user", "content": "Alice is 30, alice@example.com"}
    ]
)

# Extract the structured data
tool_use = response.content[0]
data = tool_use.input
print(data)  # {"name": "Alice", "age": 30, "email": "alice@example.com"}
```

---

## 5. Pydantic Validation Layer

### Why Validate?

JSON mode guarantees valid JSON, but not correct schema:

```python
# LLM might return
{"username": "Alice", "years": 30}  # Wrong field names!
```

### Validation Pattern

```python
from pydantic import BaseModel, ValidationError
import json

class User(BaseModel):
    name: str
    age: int

def extract_user(llm_response: str) -> User | None:
    try:
        data = json.loads(llm_response)
        return User.model_validate(data)
    except json.JSONDecodeError:
        print("Invalid JSON")
        return None
    except ValidationError as e:
        print(f"Validation failed: {e}")
        return None

# Test
result = extract_user('{"name": "Alice", "age": 30}')
print(result)  # name='Alice' age=30

result = extract_user('{"name": "Alice", "age": "thirty"}')
# Validation failed: age must be an integer
```

### Advanced Validation

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class ExtractedEntity(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    entity_type: Literal["person", "company", "location"]
    confidence: float = Field(ge=0, le=1)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip().title()

class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity]
    source_text: str

    @property
    def high_confidence_entities(self) -> list[ExtractedEntity]:
        return [e for e in self.entities if e.confidence > 0.8]
```

---

## 6. The Instructor Library

### Installation

```bash
uv add instructor
```

### Why Instructor?

Instructor wraps the OpenAI client with automatic:

- Pydantic schema injection
- Response validation
- Retry on validation failure
- Streaming support

### Basic Usage

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

# Patch the client
client = instructor.from_openai(OpenAI())

class User(BaseModel):
    name: str
    age: int

# Automatic structured output
user = client.chat.completions.create(
    model="gpt-4o",
    response_model=User,  # ← Pydantic model
    messages=[
        {"role": "user", "content": "Alice is 30 years old."}
    ]
)

print(user.name)  # Alice
print(user.age)   # 30
```

### With Retry

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, Field

client = instructor.from_openai(OpenAI())

class User(BaseModel):
    name: str = Field(description="Full name of the person")
    age: int = Field(ge=0, le=150, description="Age in years")

# Retries automatically on validation failure
user = client.chat.completions.create(
    model="gpt-4o",
    response_model=User,
    max_retries=3,  # ← Retry up to 3 times
    messages=[
        {"role": "user", "content": "Extract: Alice is 30."}
    ]
)
```

### Complex Extraction

```python
from pydantic import BaseModel, Field
from typing import Literal

class Skill(BaseModel):
    name: str
    level: Literal["beginner", "intermediate", "expert"]
    years: int = Field(ge=0)

class Experience(BaseModel):
    company: str
    role: str
    duration_months: int

class ResumeExtract(BaseModel):
    name: str
    email: str | None = None
    skills: list[Skill]
    experience: list[Experience]
    summary: str = Field(max_length=500)

resume = client.chat.completions.create(
    model="gpt-4o",
    response_model=ResumeExtract,
    messages=[
        {"role": "user", "content": f"Extract from this resume: {resume_text}"}
    ]
)
```

---

## 7. Retry Strategies

### Simple Retry with Tenacity

```python
from tenacity import retry, stop_after_attempt, retry_if_exception_type
from pydantic import ValidationError
import json

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((json.JSONDecodeError, ValidationError))
)
def extract_with_retry(prompt: str) -> User:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Return JSON with name (string) and age (integer)."},
            {"role": "user", "content": prompt}
        ]
    )

    data = json.loads(response.choices[0].message.content)
    return User.model_validate(data)
```

### Retry with Error Feedback

```python
def extract_with_feedback(prompt: str, max_retries: int = 3) -> User | None:
    messages = [
        {"role": "system", "content": "Return JSON with name (string) and age (integer)."},
        {"role": "user", "content": prompt}
    ]

    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=messages
        )

        content = response.choices[0].message.content

        try:
            data = json.loads(content)
            return User.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            # Add error feedback to messages
            messages.append({"role": "assistant", "content": content})
            messages.append({
                "role": "user",
                "content": f"That response was invalid: {e}. Please try again."
            })

    return None
```

---

## 8. Function Calling Pattern

### OpenAI Function Calling

```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_user",
            "description": "Extract user information from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "User's full name"},
                    "age": {"type": "integer", "description": "User's age"},
                    "email": {"type": "string", "description": "Email address"}
                },
                "required": ["name", "age"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Alice is 30, alice@test.com"}],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "extract_user"}}
)

# Parse the function call
tool_call = response.choices[0].message.tool_calls[0]
arguments = json.loads(tool_call.function.arguments)
print(arguments)  # {"name": "Alice", "age": 30, "email": "alice@test.com"}
```

---

## 9. Production Pattern: Extraction Pipeline

```python
from dataclasses import dataclass
from typing import TypeVar, Type
from pydantic import BaseModel
import instructor
from openai import OpenAI

T = TypeVar("T", bound=BaseModel)

@dataclass
class ExtractionResult[T]:
    data: T | None
    raw_response: str
    attempts: int
    success: bool
    error: str | None = None

class Extractor:
    def __init__(self, model: str = "gpt-4o", max_retries: int = 3):
        self.client = instructor.from_openai(OpenAI())
        self.model = model
        self.max_retries = max_retries

    def extract(
        self,
        text: str,
        schema: Type[T],
        system_prompt: str | None = None
    ) -> ExtractionResult[T]:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({
            "role": "user",
            "content": f"Extract the following information:\n\n{text}"
        })

        try:
            result = self.client.chat.completions.create(
                model=self.model,
                response_model=schema,
                max_retries=self.max_retries,
                messages=messages
            )

            return ExtractionResult(
                data=result,
                raw_response=str(result),
                attempts=1,  # Instructor handles internally
                success=True
            )

        except Exception as e:
            return ExtractionResult(
                data=None,
                raw_response="",
                attempts=self.max_retries,
                success=False,
                error=str(e)
            )

# Usage
extractor = Extractor()

class ProductInfo(BaseModel):
    name: str
    price: float
    category: str

result = extractor.extract(
    "The iPhone 15 Pro costs $999 and is a smartphone.",
    ProductInfo
)

if result.success:
    print(result.data.name)   # iPhone 15 Pro
    print(result.data.price)  # 999.0
```

---

## Quick Reference

### OpenAI JSON Mode

```python
response_format={"type": "json_object"}
# Must mention "JSON" in prompt
```

### OpenAI Structured (Beta)

```python
client.beta.chat.completions.parse(
    response_format=PydanticModel
)
```

### Instructor

```python
import instructor
client = instructor.from_openai(OpenAI())
result = client.chat.completions.create(
    response_model=PydanticModel,
    max_retries=3
)
```

### Validation Pattern

```python
try:
    data = json.loads(response)
    model = MyModel.model_validate(data)
except (JSONDecodeError, ValidationError):
    # Retry or handle error
```

---

## Summary

You've learned:

1. **JSON mode** — guarantees valid JSON
2. **Structured outputs** — schema enforcement
3. **Pydantic validation** — type safety layer
4. **Instructor** — automatic retry and validation
5. **Function calling** — alternative to JSON mode
6. **Retry strategies** — handling failures gracefully
7. **Production patterns** — extraction pipelines

Next chapter: Multimodal — Vision and Audio APIs.
