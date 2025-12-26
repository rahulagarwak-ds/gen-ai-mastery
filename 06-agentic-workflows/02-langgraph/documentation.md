# Chapter 2: LangGraph — Stateful Agent Graphs

> _"Agents need state, loops, and persistence. LangGraph provides all three."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- LangGraph core concepts (nodes, edges, state)
- Building agentic workflows
- Conditional routing
- Cycles and human-in-the-loop
- Checkpointing and persistence

---

## 1. Why LangGraph?

### The Problem with Simple Chains

```python
# Linear chains can't loop
result = step1(input) → step2(result) → step3(result)

# But agents need to:
# - Retry on failure
# - Loop until complete
# - Take different paths based on output
```

### LangGraph Solution

```
┌─────────────────────────────────────────────────────────────┐
│                      AGENT GRAPH                             │
│                                                              │
│   [START] → [PLAN] → [EXECUTE] → [EVALUATE] ──→ [END]       │
│                ↑                      │                      │
│                └──────────────────────┘                      │
│                     (if not done)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Installation

```bash
uv add langgraph
```

---

## 3. Core Concepts

### State

```python
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    current_step: str
    iteration: int
```

### Nodes

```python
def planner(state: AgentState) -> AgentState:
    """Node that plans next action."""
    return {"current_step": "execute"}

def executor(state: AgentState) -> AgentState:
    """Node that executes actions."""
    return {"iteration": state["iteration"] + 1}
```

### Edges

```python
def should_continue(state: AgentState) -> str:
    """Decide next node based on state."""
    if state["iteration"] >= 3:
        return "end"
    return "planner"
```

---

## 4. Building a Graph

### Basic Structure

```python
from langgraph.graph import StateGraph, END

# Create graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", planner)
workflow.add_node("executor", executor)

# Add edges
workflow.add_edge("planner", "executor")
workflow.add_conditional_edges(
    "executor",
    should_continue,
    {"planner": "planner", "end": END}
)

# Set entry point
workflow.set_entry_point("planner")

# Compile
app = workflow.compile()
```

### Running the Graph

```python
# Initial state
initial_state = {
    "messages": [],
    "current_step": "start",
    "iteration": 0
}

# Run
final_state = app.invoke(initial_state)
print(final_state)

# Stream steps
for event in app.stream(initial_state):
    print(event)
```

---

## 5. ReAct Agent Pattern

```python
from openai import OpenAI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class ReActState(TypedDict):
    messages: Annotated[list, add_messages]
    tool_calls: list

client = OpenAI()

tools = [
    {"type": "function", "function": {"name": "search", "parameters": {...}}}
]

def agent(state: ReActState) -> ReActState:
    """Call LLM with tools."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=state["messages"],
        tools=tools
    )
    return {
        "messages": [response.choices[0].message],
        "tool_calls": response.choices[0].message.tool_calls or []
    }

def execute_tools(state: ReActState) -> ReActState:
    """Execute tool calls."""
    results = []
    for call in state["tool_calls"]:
        result = run_tool(call.function.name, call.function.arguments)
        results.append({
            "tool_call_id": call.id,
            "role": "tool",
            "content": result
        })
    return {"messages": results, "tool_calls": []}

def router(state: ReActState) -> str:
    """Route based on tool calls."""
    if state["tool_calls"]:
        return "tools"
    return END

# Build graph
workflow = StateGraph(ReActState)
workflow.add_node("agent", agent)
workflow.add_node("tools", execute_tools)
workflow.add_conditional_edges("agent", router, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")
workflow.set_entry_point("agent")

agent_runner = workflow.compile()
```

---

## 6. Human-in-the-Loop

### Interrupt Pattern

```python
from langgraph.checkpoint.memory import MemorySaver

# Add checkpointing
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer, interrupt_before=["executor"])

# Run until interrupt
config = {"configurable": {"thread_id": "1"}}
for event in app.stream(initial_state, config):
    print(event)
# Pauses before executor

# User approves, continue
for event in app.stream(None, config):
    print(event)
```

### Human Approval Node

```python
def needs_approval(state: AgentState) -> str:
    if state.get("requires_approval"):
        return "wait_for_human"
    return "execute"

workflow.add_conditional_edges("planner", needs_approval)
```

---

## 7. Persistence

### Memory Checkpointer

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Run with thread ID
config = {"configurable": {"thread_id": "conversation_1"}}
result = app.invoke(input, config)

# Resume later
history = app.get_state(config)
print(history.values)
```

### SQLite Checkpointer

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string(":memory:") as checkpointer:
    app = workflow.compile(checkpointer=checkpointer)
```

---

## 8. Subgraphs

### Composing Graphs

```python
# Inner graph
inner_workflow = StateGraph(InnerState)
inner_workflow.add_node(...)
inner_app = inner_workflow.compile()

# Outer graph uses inner
def inner_node(state):
    inner_result = inner_app.invoke(state)
    return inner_result

outer_workflow = StateGraph(OuterState)
outer_workflow.add_node("inner", inner_node)
```

---

## 9. Streaming

### Token Streaming

```python
async for event in app.astream_events(
    initial_state,
    version="v2"
):
    if event["event"] == "on_chat_model_stream":
        print(event["data"]["chunk"].content, end="")
```

### Node Updates

```python
for event in app.stream(initial_state, stream_mode="updates"):
    node_name = list(event.keys())[0]
    print(f"Node: {node_name}, Output: {event[node_name]}")
```

---

## Quick Reference

### State

```python
class MyState(TypedDict):
    messages: Annotated[list, add_messages]
```

### Graph

```python
workflow = StateGraph(MyState)
workflow.add_node("name", function)
workflow.add_edge("from", "to")
workflow.add_conditional_edges("from", router, {"a": "a", "b": "b"})
app = workflow.compile()
```

### Run

```python
result = app.invoke(initial_state)
for event in app.stream(initial_state):
    ...
```

---

## Summary

You've learned:

1. **State** — Managing agent data
2. **Nodes & Edges** — Graph structure
3. **Conditional routing** — Dynamic paths
4. **Cycles** — ReAct loops
5. **Human-in-the-loop** — Interrupts
6. **Persistence** — Checkpointing

Next chapter: Multi-Agent — Coordination and hierarchies.
