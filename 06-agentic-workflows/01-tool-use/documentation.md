# Chapter 1: Tool Use — Giving LLMs Superpowers

> _"An LLM without tools is just a chatbot. With tools, it's an agent."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Function calling with OpenAI and Anthropic
- Tool schema design
- Execution patterns (single, parallel, sequential)
- Error handling and validation
- Building a tool registry

---

## 1. What is Tool Use?

### The Concept

```
User Query: "What's the weather in Tokyo?"

Without Tools:
  LLM → "I don't have real-time weather data."

With Tools:
  LLM → calls get_weather("Tokyo") → API returns 72°F
      → "The weather in Tokyo is 72°F and sunny."
```

### How It Works

```
┌──────────────────────────────────────────────────────────────┐
│                         TOOL USE FLOW                        │
├──────────────────────────────────────────────────────────────┤
│  1. User Query + Tool Definitions → LLM                       │
│  2. LLM decides which tool(s) to call with arguments          │
│  3. Your code executes the tool(s)                           │
│  4. Tool results → LLM                                       │
│  5. LLM generates final response                             │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. OpenAI Function Calling

### Tool Definition

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country, e.g., 'Tokyo, Japan'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### Making the Call

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto"  # or "required" to force tool use
)

message = response.choices[0].message

if message.tool_calls:
    for call in message.tool_calls:
        print(f"Tool: {call.function.name}")
        print(f"Args: {call.function.arguments}")
```

### Executing and Continuing

```python
def get_weather(location: str, unit: str = "celsius") -> dict:
    # Real implementation would call weather API
    return {"temperature": 22, "condition": "sunny", "unit": unit}

def process_tool_calls(message):
    results = []
    for call in message.tool_calls:
        args = json.loads(call.function.arguments)

        if call.function.name == "get_weather":
            result = get_weather(**args)
        else:
            result = {"error": "Unknown function"}

        results.append({
            "tool_call_id": call.id,
            "role": "tool",
            "content": json.dumps(result)
        })
    return results

# Continue conversation with tool results
tool_results = process_tool_calls(message)

final_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "What's the weather in Tokyo?"},
        message,  # Assistant message with tool_calls
        *tool_results  # Tool results
    ]
)

print(final_response.choices[0].message.content)
```

---

## 3. Anthropic Tool Use

### Tool Definition

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country"
                }
            },
            "required": ["location"]
        }
    }
]
```

### Making the Call

```python
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}]
)

# Check if tool use requested
for block in response.content:
    if block.type == "tool_use":
        print(f"Tool: {block.name}")
        print(f"Args: {block.input}")
        print(f"ID: {block.id}")
```

### Continuing with Results

```python
# Execute tool
tool_result = get_weather(**block.input)

# Continue conversation
final = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"},
        {"role": "assistant", "content": response.content},
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(tool_result)
            }]
        }
    ]
)
```

---

## 4. Tool Schema Patterns

### With Pydantic

```python
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(description="City and country")
    unit: str = Field(default="celsius", description="Temperature unit")

def pydantic_to_tool_schema(model: type[BaseModel]) -> dict:
    """Convert Pydantic model to OpenAI tool schema."""
    schema = model.model_json_schema()
    return {
        "type": "function",
        "function": {
            "name": model.__name__.lower().replace("input", ""),
            "description": model.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        }
    }
```

### Tool Decorator

```python
from functools import wraps
from typing import Callable
import inspect

def tool(description: str):
    """Decorator to mark a function as a tool."""
    def decorator(func: Callable):
        func._is_tool = True
        func._description = description

        # Generate schema from type hints
        hints = func.__annotations__
        sig = inspect.signature(func)

        properties = {}
        required = []

        for name, param in sig.parameters.items():
            if name == "return":
                continue
            hint = hints.get(name, str)
            properties[name] = {
                "type": "string" if hint == str else "number" if hint in (int, float) else "object",
                "description": ""
            }
            if param.default == inspect.Parameter.empty:
                required.append(name)

        func._schema = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

        return func
    return decorator

@tool("Search the web for information")
def web_search(query: str) -> str:
    return f"Results for: {query}"
```

---

## 5. Tool Registry

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}

    def register(self, func: Callable):
        """Register a tool function."""
        self._tools[func.__name__] = func
        return func

    def get_schemas(self) -> list[dict]:
        """Get all tool schemas for LLM."""
        return [f._schema for f in self._tools.values() if hasattr(f, "_schema")]

    def execute(self, name: str, args: dict) -> any:
        """Execute a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name](**args)

    def process_calls(self, tool_calls: list) -> list[dict]:
        """Process all tool calls and return results."""
        results = []
        for call in tool_calls:
            try:
                args = json.loads(call.function.arguments)
                result = self.execute(call.function.name, args)
                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "content": json.dumps(result)
                })
            except Exception as e:
                results.append({
                    "tool_call_id": call.id,
                    "role": "tool",
                    "content": json.dumps({"error": str(e)})
                })
        return results

registry = ToolRegistry()

@registry.register
@tool("Calculate mathematical expressions")
def calculate(expression: str) -> float:
    return eval(expression)  # Use safer evaluation in production!
```

---

## 6. Parallel Tool Calls

```python
# OpenAI can request multiple tools in parallel
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user",
        "content": "What's the weather in Tokyo, London, and New York?"
    }],
    tools=tools
)

# May receive 3 tool calls
for call in response.choices[0].message.tool_calls:
    print(f"{call.function.name}({call.function.arguments})")

# Execute all in parallel
import asyncio

async def execute_parallel(calls):
    tasks = [
        asyncio.to_thread(registry.execute, c.function.name, json.loads(c.function.arguments))
        for c in calls
    ]
    return await asyncio.gather(*tasks)
```

---

## 7. Common Tools

### Web Search

```python
@tool("Search the web")
def web_search(query: str, num_results: int = 5) -> list[dict]:
    # Use SerpAPI, Tavily, or similar
    pass

### Code Execution

@tool("Execute Python code")
def run_python(code: str) -> str:
    # Use sandboxed execution (e.g., Docker)
    pass

### Database Query

@tool("Query the database")
def query_db(sql: str) -> list[dict]:
    # Execute read-only SQL
    pass
```

---

## Quick Reference

### OpenAI

```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    tools=[{"type": "function", "function": {...}}]
)
```

### Anthropic

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=[{"name": ..., "input_schema": {...}}],
    messages=[...]
)
```

### Execute

```python
result = registry.execute(call.function.name, json.loads(call.function.arguments))
```

---

## Summary

You've learned:

1. **Function calling** — OpenAI and Anthropic APIs
2. **Tool schemas** — Defining tool interfaces
3. **Execution** — Running tools safely
4. **Patterns** — Decorators, registries
5. **Parallel calls** — Multiple tools at once

Next chapter: LangGraph — Stateful agent workflows.
