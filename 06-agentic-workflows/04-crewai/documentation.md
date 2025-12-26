# Chapter 4: CrewAI — Multi-Agent Framework

> _"The whole is greater than the sum of its parts."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- CrewAI architecture (Agents, Tasks, Crews)
- Agent creation with roles and goals
- Task definition and dependencies
- Process types (sequential, hierarchical)
- Tool integration for agents

---

## 1. CrewAI Basics

### Installation

```bash
uv add crewai crewai-tools
```

### Core Concepts

```
┌─────────────────────────────────────┐
│               CREW                   │
│  ┌─────────┐  ┌─────────┐          │
│  │ AGENT 1 │  │ AGENT 2 │  ...     │
│  │ (Role)  │  │ (Role)  │          │
│  └────┬────┘  └────┬────┘          │
│       │            │                │
│  ┌────▼────┐  ┌────▼────┐          │
│  │ TASK A  │──│ TASK B  │  ...     │
│  └─────────┘  └─────────┘          │
└─────────────────────────────────────┘
```

- **Agent**: An autonomous unit with a role, goal, and backstory
- **Task**: A specific job to be done by an agent
- **Crew**: A team of agents working together on tasks
- **Process**: How tasks are executed (sequential/hierarchical)

---

## 2. Creating Agents

### Basic Agent

```python
from crewai import Agent

researcher = Agent(
    role="Research Analyst",
    goal="Find accurate and comprehensive information on any topic",
    backstory="""You are a senior research analyst with 10 years of
    experience. You excel at finding detailed, accurate information
    and synthesizing it into clear insights.""",
    verbose=True,
    allow_delegation=False  # Can this agent delegate to others?
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging, well-structured content",
    backstory="""You are a professional content writer known for
    creating clear, compelling articles that explain complex topics
    simply.""",
    verbose=True
)
```

### Agent with LLM Configuration

```python
from crewai import Agent, LLM

# Custom LLM
llm = LLM(
    model="gpt-4o",
    temperature=0.7
)

analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="Expert data analyst...",
    llm=llm
)
```

### Agent with Memory

```python
agent = Agent(
    role="Customer Support",
    goal="Help customers effectively",
    backstory="...",
    memory=True,  # Enable memory between tasks
    max_iter=5,   # Max reasoning iterations
    max_rpm=10    # Rate limiting
)
```

---

## 3. Defining Tasks

### Basic Task

```python
from crewai import Task

research_task = Task(
    description="""Research the topic: {topic}

    Find:
    1. Key facts and statistics
    2. Recent developments
    3. Expert opinions

    Provide a comprehensive summary.""",
    expected_output="A detailed research report with sources",
    agent=researcher
)

writing_task = Task(
    description="""Write an article based on this research: {research}

    The article should be:
    - 500-800 words
    - Easy to understand
    - Well-structured with headers""",
    expected_output="A polished article ready for publication",
    agent=writer
)
```

### Task Dependencies

```python
# writing_task depends on research_task output
writing_task = Task(
    description="Write article based on research",
    expected_output="Article",
    agent=writer,
    context=[research_task]  # Will receive output from research_task
)
```

### Task with Tools

```python
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

research_task = Task(
    description="Research {topic} using web search",
    expected_output="Research findings",
    agent=researcher,
    tools=[search_tool, scrape_tool]
)
```

---

## 4. Building Crews

### Sequential Crew

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # Tasks run in order
    verbose=True
)

# Run the crew
result = crew.kickoff(inputs={"topic": "AI in Healthcare"})
print(result.raw)
```

### Hierarchical Crew

```python
# Manager agent coordinates others
manager = Agent(
    role="Project Manager",
    goal="Coordinate the team to deliver quality output",
    backstory="Senior PM with tech background...",
    allow_delegation=True
)

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.hierarchical,
    manager_agent=manager
)
```

### Crew with Memory

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # Enable crew-level memory
    embedder={
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"}
    }
)
```

---

## 5. CrewAI Tools

### Built-in Tools

```python
from crewai_tools import (
    SerperDevTool,      # Web search
    ScrapeWebsiteTool,  # Web scraping
    FileReadTool,       # Read files
    DirectoryReadTool,  # List directory
    CodeInterpreterTool # Execute code
)

# Web search
search = SerperDevTool()

# File operations
file_reader = FileReadTool(file_path="./data/report.txt")
dir_reader = DirectoryReadTool(directory="./documents")
```

### Custom Tool

```python
from crewai.tools import BaseTool
from pydantic import Field

class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "Performs mathematical calculations"

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {e}"

# Use in agent
math_agent = Agent(
    role="Math Assistant",
    goal="Help with calculations",
    backstory="...",
    tools=[CalculatorTool()]
)
```

### Tool from Function

```python
from crewai.tools import tool

@tool("Weather Lookup")
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # API call here
    return f"Weather in {city}: 72°F, Sunny"

agent = Agent(
    role="Travel Assistant",
    tools=[get_weather]
)
```

---

## 6. Practical Patterns

### Research and Write Crew

```python
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

def create_content_crew(topic: str):
    # Agents
    researcher = Agent(
        role="Researcher",
        goal="Find comprehensive information",
        backstory="Expert researcher...",
        tools=[SerperDevTool()]
    )

    writer = Agent(
        role="Writer",
        goal="Create engaging content",
        backstory="Professional writer..."
    )

    editor = Agent(
        role="Editor",
        goal="Ensure quality and accuracy",
        backstory="Senior editor..."
    )

    # Tasks
    research = Task(
        description=f"Research: {topic}",
        expected_output="Detailed research notes",
        agent=researcher
    )

    write = Task(
        description="Write article from research",
        expected_output="Draft article",
        agent=writer,
        context=[research]
    )

    edit = Task(
        description="Edit and polish the article",
        expected_output="Final article",
        agent=editor,
        context=[write]
    )

    return Crew(
        agents=[researcher, writer, editor],
        tasks=[research, write, edit],
        process=Process.sequential
    )

# Run
crew = create_content_crew("Future of Renewable Energy")
result = crew.kickoff()
```

### Customer Support Crew

```python
def create_support_crew():
    # Triage agent
    triage = Agent(
        role="Support Triage",
        goal="Categorize and prioritize customer issues",
        backstory="Experienced support lead..."
    )

    # Technical support
    tech = Agent(
        role="Technical Support",
        goal="Resolve technical issues",
        backstory="Senior developer..."
    )

    # Customer success
    success = Agent(
        role="Customer Success",
        goal="Ensure customer satisfaction",
        backstory="Customer success manager..."
    )

    categorize = Task(
        description="Analyze: {issue} and categorize",
        expected_output="Category and priority",
        agent=triage
    )

    resolve = Task(
        description="Resolve the issue based on category",
        expected_output="Resolution steps",
        agent=tech,
        context=[categorize]
    )

    follow_up = Task(
        description="Create follow-up plan",
        expected_output="Customer follow-up message",
        agent=success,
        context=[resolve]
    )

    return Crew(
        agents=[triage, tech, success],
        tasks=[categorize, resolve, follow_up],
        process=Process.sequential
    )
```

---

## 7. CrewAI vs LangGraph

| Feature        | CrewAI              | LangGraph         |
| -------------- | ------------------- | ----------------- |
| Abstraction    | High (agents/tasks) | Low (nodes/edges) |
| Learning curve | Easier              | Steeper           |
| Flexibility    | Structured patterns | Full control      |
| Best for       | Standard workflows  | Custom logic      |
| Multi-agent    | Built-in            | Manual setup      |

### When to Use Each

- **CrewAI**: Standard multi-agent patterns, quick prototyping
- **LangGraph**: Custom control flow, complex state machines

---

## Quick Reference

### Create Agent

```python
agent = Agent(role="...", goal="...", backstory="...")
```

### Create Task

```python
task = Task(description="...", expected_output="...", agent=agent)
```

### Run Crew

```python
crew = Crew(agents=[...], tasks=[...], process=Process.sequential)
result = crew.kickoff(inputs={...})
```

---

## Summary

You've learned:

1. **Agents** — Autonomous units with roles and goals
2. **Tasks** — Specific jobs with dependencies
3. **Crews** — Teams executing workflows
4. **Tools** — Extending agent capabilities
5. **Patterns** — Research, content, support crews

CrewAI provides a high-level framework for multi-agent systems.
