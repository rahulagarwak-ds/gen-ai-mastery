# Mini Project: Research Crew

## 🎯 Objective

Build a multi-agent research crew that searches, analyzes, and summarizes topics.

---

## 📋 Requirements

### 1. Agents

```python
from crewai import Agent
from crewai_tools import SerperDevTool

def create_research_agents():
    """Create the research crew agents."""

    searcher = Agent(
        role="Web Searcher",
        goal="Find relevant sources and information",
        backstory="Expert at finding information online...",
        tools=[SerperDevTool()]
    )

    analyst = Agent(
        role="Research Analyst",
        goal="Analyze and synthesize information",
        backstory="Skilled at extracting insights..."
    )

    writer = Agent(
        role="Report Writer",
        goal="Create clear, actionable reports",
        backstory="Technical writer who excels at clarity..."
    )

    return searcher, analyst, writer
```

### 2. Tasks

```python
from crewai import Task

def create_research_tasks(topic: str, searcher, analyst, writer):
    """Create the research workflow tasks."""

    search = Task(
        description=f"Search for: {topic}. Find 5+ relevant sources.",
        expected_output="List of sources with summaries",
        agent=searcher
    )

    analyze = Task(
        description="Analyze the sources and extract key insights",
        expected_output="Analysis with key findings and patterns",
        agent=analyst,
        context=[search]
    )

    write = Task(
        description="Write a comprehensive research report",
        expected_output="Structured report with sections",
        agent=writer,
        context=[analyze]
    )

    return [search, analyze, write]
```

### 3. Research Crew

```python
from crewai import Crew, Process

class ResearchCrew:
    def __init__(self):
        self.searcher, self.analyst, self.writer = create_research_agents()

    def research(self, topic: str) -> str:
        """Run research on a topic."""
        tasks = create_research_tasks(
            topic,
            self.searcher,
            self.analyst,
            self.writer
        )

        crew = Crew(
            agents=[self.searcher, self.analyst, self.writer],
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result.raw

    def research_with_questions(
        self,
        topic: str,
        questions: list[str]
    ) -> dict:
        """Research topic with specific questions."""
        pass
```

---

## ✅ Test Cases

```python
crew = ResearchCrew()

# Basic research
report = crew.research("Impact of AI on Healthcare")
assert len(report) > 500
assert "AI" in report or "healthcare" in report.lower()

# Research with questions
result = crew.research_with_questions(
    topic="Electric Vehicles",
    questions=[
        "What is the current market share?",
        "What are the main challenges?",
        "What are future predictions?"
    ]
)
assert all(q in result for q in ["market", "challenges", "future"])
```

---

## 🎁 Bonus

1. Add a fact-checker agent
2. Enable memory for follow-up questions
3. Output in different formats (markdown, JSON)
4. Add source citation tracking

**Time estimate:** 3-4 hours
