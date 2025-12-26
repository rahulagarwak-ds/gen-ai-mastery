# 🏆 Month 6 Capstone: AI Research Assistant

## 🎯 Objective

Build a multi-agent research assistant that can:

- Search the web for information
- Execute Python code
- Read and write files
- Synthesize findings into reports

---

## 📋 Requirements

### 1. Tools

```python
# Web Search
@tool("Search the web")
def web_search(query: str) -> list[dict]:
    pass

# Code Execution
@tool("Run Python code")
def run_code(code: str) -> str:
    pass

# File Operations
@tool("Read a file")
def read_file(path: str) -> str:
    pass

@tool("Write to file")
def write_file(path: str, content: str) -> str:
    pass
```

### 2. Agents

```python
# Research Agent
# - Uses web_search
# - Synthesizes findings

# Code Agent
# - Uses run_code
# - Analyzes data

# Writer Agent
# - Uses write_file
# - Creates reports

# Supervisor
# - Routes to appropriate agent
# - Manages workflow
```

### 3. State

```python
class AssistantState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    research_findings: list[str]
    code_results: list[str]
    final_report: str
    next_agent: str
```

### 4. CLI Interface

```bash
# Interactive mode
research-assistant chat

# Single query
research-assistant query "Research the latest AI trends and write a report"

# With output file
research-assistant query "..." --output report.md
```

---

## 📁 Project Structure

```
research_assistant/
├── __init__.py
├── tools/
│   ├── search.py
│   ├── code.py
│   └── files.py
├── agents/
│   ├── researcher.py
│   ├── coder.py
│   ├── writer.py
│   └── supervisor.py
├── graph.py          # LangGraph workflow
├── state.py          # State definitions
└── cli.py            # CLI interface
```

---

## ✅ Test Cases

```python
# Initialize assistant
assistant = ResearchAssistant()

# Simple research
result = assistant.run("What is the capital of France?")
assert "Paris" in result

# Research + report
result = assistant.run(
    "Research Python web frameworks and create a comparison report"
)
assert "report" in result.lower()
assert len(assistant.state["research_findings"]) > 0

# Code execution
result = assistant.run(
    "Calculate π to 10 decimal places using Python"
)
assert "3.14159" in result
```

---

## 🏆 Bonus

1. **Memory**: Remember previous conversations
2. **Human-in-loop**: Ask for approval before actions
3. **Streaming**: Stream agent thinking process
4. **Web UI**: Streamlit/Gradio interface
5. **Plugins**: Allow adding new tools dynamically

**Time estimate:** 6-10 hours

---

## 💡 Hints

<details>
<summary>Hint 1: Safe Code Execution</summary>

```python
import subprocess

def run_code_safe(code: str) -> str:
    result = subprocess.run(
        ["python", "-c", code],
        capture_output=True,
        timeout=30,
        text=True
    )
    return result.stdout or result.stderr
```

</details>

<details>
<summary>Hint 2: Web Search</summary>

```python
# Use Tavily for search
from tavily import TavilyClient

client = TavilyClient(api_key="...")
results = client.search(query)
```

</details>

---

## 🎓 Roadmap Complete!

Congratulations! You've completed the Gen AI Mastery roadmap:

- ✅ Month 1: Python Foundation
- ✅ Month 2: LLM Interface
- ✅ Month 3: RAG Fundamentals
- ✅ Month 4: Backend Engineering
- ✅ Month 5: Evaluation & Ops
- ✅ Month 6: Agentic Workflows

You're now equipped to build production-grade AI applications!
