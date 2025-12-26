# Mini Project: Prompt Registry

## 🎯 Objective

Build a version-controlled prompt management system.

---

## 📋 Requirements

### 1. Prompt Model

```python
from dataclasses import dataclass

@dataclass
class Prompt:
    name: str
    version: str
    system: str
    user_template: str
    model: str = "gpt-4o"
    temperature: float = 0.7

def load_prompt(path: str) -> Prompt:
    """Load prompt from YAML."""
    pass
```

### 2. Registry

```python
class PromptRegistry:
    def __init__(self, prompts_dir: str = "./prompts"):
        pass

    def get(self, name: str, version: str = "latest") -> Prompt:
        """Get prompt by name and version."""
        pass

    def list(self) -> list[str]:
        """List all prompt names."""
        pass

    def get_versions(self, name: str) -> list[str]:
        """List versions for a prompt."""
        pass

    def render(self, name: str, **kwargs) -> list[dict]:
        """Render prompt as messages."""
        pass
```

### 3. CLI

```bash
# List prompts
prompt-registry list

# Show prompt
prompt-registry show summarize

# Render with variables
prompt-registry render summarize --text "Hello world"

# Compare versions
prompt-registry diff summarize v1.0.0 v1.1.0
```

---

## ✅ Test Cases

```python
registry = PromptRegistry("./prompts")

# Get prompt
prompt = registry.get("summarize")
assert prompt.version is not None

# List
prompts = registry.list()
assert "summarize" in prompts

# Render
messages = registry.render("summarize", text="Hello")
assert len(messages) == 2
assert "Hello" in messages[1]["content"]
```

**Time estimate:** 2-3 hours
