# Chapter 3: Multi-Agent Systems — Coordination at Scale

> _"One agent is powerful. Multiple agents are unstoppable."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Multi-agent architectures
- Agent coordination patterns
- Handoffs and routing
- Supervisor-worker hierarchies
- Building multi-agent systems with LangGraph

---

## 1. Why Multi-Agent?

### Single Agent Limitations

```
User: "Research this topic, write an article, and post it to Twitter"

Single Agent: Gets confused trying to do everything at once
```

### Multi-Agent Advantage

```
Coordinator → Research Agent → Writer Agent → Social Agent
      ↑                                              │
      └──────────────────────────────────────────────┘
                    (reports completion)
```

---

## 2. Architecture Patterns

### Supervisor Pattern

```
┌─────────────────────────────────────────────┐
│                 SUPERVISOR                   │
│         (decides which agent to call)        │
├─────────────────────────────────────────────┤
│      ↓              ↓              ↓         │
│  [Researcher]   [Writer]      [Coder]       │
│      ↓              ↓              ↓         │
│  (results)      (results)     (results)     │
└─────────────────────────────────────────────┘
```

### Hierarchical Pattern

```
┌─────────────────────────────────────────────┐
│              ORCHESTRATOR                    │
│                   ↓                          │
│     ┌─────────────┼─────────────┐           │
│     ↓             ↓             ↓           │
│ [Research     [Content      [Publish        │
│  Team]         Team]         Team]          │
│   ↓ ↓           ↓ ↓           ↓ ↓           │
│ [Web] [Docs]  [Write][Edit] [Format][Post]  │
└─────────────────────────────────────────────┘
```

### Sequential Handoff

```
[Agent A] → [Agent B] → [Agent C] → [Result]
```

---

## 3. Agent Definition

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str
    results: dict

def create_agent(name: str, system_prompt: str, tools: list = None):
    """Factory for creating specialized agents."""

    def agent_node(state: AgentState) -> AgentState:
        messages = [
            {"role": "system", "content": system_prompt},
            *state["messages"]
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools
        )

        return {
            "messages": [response.choices[0].message],
            "results": {name: response.choices[0].message.content}
        }

    return agent_node

researcher = create_agent(
    "researcher",
    "You are a research specialist. Find relevant information."
)

writer = create_agent(
    "writer",
    "You are a skilled writer. Create clear, engaging content."
)
```

---

## 4. Supervisor Agent

```python
SUPERVISOR_PROMPT = """You are a supervisor managing these agents:
- researcher: Gathers information
- writer: Writes content
- coder: Writes code

Based on the conversation, decide which agent should act next.
Respond with ONLY the agent name or "FINISH" if done."""

def supervisor(state: AgentState) -> AgentState:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SUPERVISOR_PROMPT},
            *state["messages"]
        ]
    )

    next_agent = response.choices[0].message.content.strip().lower()

    return {"next_agent": next_agent}

def route_supervisor(state: AgentState) -> str:
    next_agent = state.get("next_agent", "finish")
    if next_agent == "finish":
        return "end"
    return next_agent
```

---

## 5. Building Multi-Agent Graph

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("supervisor", supervisor)
workflow.add_node("researcher", researcher)
workflow.add_node("writer", writer)
workflow.add_node("coder", coder)

# Routes from supervisor
workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "researcher": "researcher",
        "writer": "writer",
        "coder": "coder",
        "end": END
    }
)

# All agents return to supervisor
for agent in ["researcher", "writer", "coder"]:
    workflow.add_edge(agent, "supervisor")

# Entry point
workflow.set_entry_point("supervisor")

multi_agent = workflow.compile()
```

---

## 6. Handoff Pattern

```python
class HandoffState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    handoff_to: str | None

def agent_with_handoff(name: str, next_candidates: list[str]):
    """Create agent that can hand off to others."""

    handoff_tool = {
        "type": "function",
        "function": {
            "name": "handoff",
            "description": "Transfer to another agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_agent": {
                        "type": "string",
                        "enum": next_candidates,
                        "description": "Agent to hand off to"
                    },
                    "context": {
                        "type": "string",
                        "description": "Context for the next agent"
                    }
                },
                "required": ["to_agent"]
            }
        }
    }

    def node(state: HandoffState) -> HandoffState:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=state["messages"],
            tools=[handoff_tool]
        )

        handoff_to = None
        if response.choices[0].message.tool_calls:
            call = response.choices[0].message.tool_calls[0]
            if call.function.name == "handoff":
                args = json.loads(call.function.arguments)
                handoff_to = args["to_agent"]

        return {
            "messages": [response.choices[0].message],
            "handoff_to": handoff_to
        }

    return node
```

---

## 7. Communication Patterns

### Shared State

```python
# All agents read/write to shared state
class SharedState(TypedDict):
    messages: list
    research_findings: list
    draft_content: str
    final_output: str
```

### Message Passing

```python
# Agents communicate via messages
def send_to_agent(state: AgentState, target: str, message: str):
    return {
        "messages": [{
            "role": "system",
            "content": f"[From {state['current_agent']} to {target}]: {message}"
        }]
    }
```

---

## 8. Example: Research Team

```python
# Specialized agents
search_agent = create_agent(
    "search",
    "Search the web for relevant information.",
    tools=[web_search_tool]
)

summarize_agent = create_agent(
    "summarize",
    "Summarize the research findings."
)

fact_check_agent = create_agent(
    "fact_check",
    "Verify the accuracy of claims."
)

# Build team workflow
team = StateGraph(AgentState)
team.add_node("search", search_agent)
team.add_node("summarize", summarize_agent)
team.add_node("fact_check", fact_check_agent)

team.add_edge("search", "summarize")
team.add_edge("summarize", "fact_check")
team.add_edge("fact_check", END)

team.set_entry_point("search")
research_team = team.compile()
```

---

## Quick Reference

### Create Agent

```python
agent = create_agent(name, system_prompt, tools)
```

### Supervisor Routing

```python
workflow.add_conditional_edges("supervisor", router, {...})
```

### Agent → Supervisor

```python
workflow.add_edge("agent", "supervisor")
```

---

## Summary

You've learned:

1. **Patterns** — Supervisor, hierarchical, sequential
2. **Agent factory** — Create specialized agents
3. **Supervisor** — Central coordination
4. **Handoffs** — Agent-to-agent transfer
5. **Teams** — Subgraphs for teams

**Month 6 Complete!** You can now build sophisticated AI agent systems.
