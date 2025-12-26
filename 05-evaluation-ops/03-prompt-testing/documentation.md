# Chapter 3: Prompt Testing — Version Control and Regression

> _"Your prompts are code. Treat them that way."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Prompt versioning strategies
- Regression testing for prompts
- A/B testing prompts in production
- Prompt management libraries
- CI/CD for prompts

---

## 1. Why Version Prompts?

### The Problem

```python
# This works today...
PROMPT = "Summarize this text: {text}"

# Someone changes it...
PROMPT = "Create a brief summary: {text}"

# And everything breaks.
```

### What to Track

| Aspect      | Why                                  |
| ----------- | ------------------------------------ |
| Prompt text | Changes affect output                |
| Model       | Different models = different results |
| Parameters  | Temperature, max_tokens matter       |
| Examples    | Few-shot affects quality             |

---

## 2. Prompt as Code

### Configuration File

```yaml
# prompts/summarize.yaml
name: summarize
version: '1.2.0'
model: gpt-4o
temperature: 0.3
max_tokens: 500

system: |
  You are a professional summarizer.
  Create concise, accurate summaries.

user_template: |
  Summarize the following text in {length} sentences:

  {text}

examples:
  - input: 'Long article about Python...'
    output: 'Python is a programming language...'
```

### Prompt Loader

```python
import yaml
from dataclasses import dataclass

@dataclass
class Prompt:
    name: str
    version: str
    model: str
    system: str
    user_template: str
    temperature: float = 0.7
    max_tokens: int = 1000

def load_prompt(name: str) -> Prompt:
    with open(f"prompts/{name}.yaml") as f:
        data = yaml.safe_load(f)
    return Prompt(**data)

def render_prompt(prompt: Prompt, **kwargs) -> list[dict]:
    return [
        {"role": "system", "content": prompt.system},
        {"role": "user", "content": prompt.user_template.format(**kwargs)}
    ]
```

---

## 3. Regression Testing

### Test Format

```yaml
# tests/summarize_tests.yaml
tests:
  - id: test_basic_summary
    inputs:
      text: 'Python is a high-level programming language...'
      length: 2
    assertions:
      - type: contains
        value: 'Python'
      - type: max_length
        value: 500

  - id: test_handles_empty
    inputs:
      text: ''
      length: 1
    assertions:
      - type: not_empty
```

### Test Runner

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Assertion:
    type: str
    value: any

def check_assertion(response: str, assertion: Assertion) -> bool:
    if assertion.type == "contains":
        return assertion.value.lower() in response.lower()
    elif assertion.type == "max_length":
        return len(response) <= assertion.value
    elif assertion.type == "not_empty":
        return len(response.strip()) > 0
    elif assertion.type == "min_words":
        return len(response.split()) >= assertion.value
    return True

def run_prompt_tests(
    prompt: Prompt,
    test_file: str,
    runner: Callable
) -> dict:
    """Run regression tests on a prompt."""
    with open(test_file) as f:
        tests = yaml.safe_load(f)["tests"]

    results = {"passed": 0, "failed": 0, "errors": []}

    for test in tests:
        try:
            messages = render_prompt(prompt, **test["inputs"])
            response = runner(messages)

            all_passed = all(
                check_assertion(response, Assertion(**a))
                for a in test["assertions"]
            )

            if all_passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "test_id": test["id"],
                    "response": response[:100]
                })
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "test_id": test["id"],
                "error": str(e)
            })

    return results
```

---

## 4. A/B Testing

### Experiment Framework

```python
import random
from dataclasses import dataclass
from typing import Optional

@dataclass
class Experiment:
    name: str
    control: Prompt
    variant: Prompt
    traffic_percent: float = 0.5

experiments: dict[str, Experiment] = {}

def get_prompt(experiment_name: str, user_id: str) -> tuple[Prompt, str]:
    """Get prompt based on experiment assignment."""
    exp = experiments.get(experiment_name)

    if not exp:
        return load_prompt(experiment_name), "default"

    # Consistent assignment per user
    assignment = hash(f"{experiment_name}:{user_id}") % 100

    if assignment < exp.traffic_percent * 100:
        return exp.variant, "variant"
    return exp.control, "control"
```

### Logging Experiments

```python
def log_experiment(
    experiment: str,
    variant: str,
    user_id: str,
    query: str,
    response: str,
    feedback: Optional[float] = None
):
    """Log experiment data for analysis."""
    entry = {
        "experiment": experiment,
        "variant": variant,
        "user_id": user_id,
        "query": query,
        "response": response,
        "feedback": feedback,
        "timestamp": datetime.utcnow().isoformat()
    }
    # Send to analytics
```

---

## 5. Prompt Management Libraries

### PromptLayer

```python
# pip install promptlayer
import promptlayer
promptlayer.api_key = "..."

openai = promptlayer.openai

# Automatically logs all calls
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    pl_tags=["production", "summarize"]
)
```

### Custom Registry

```python
from pathlib import Path
import hashlib

class PromptRegistry:
    def __init__(self, prompts_dir: str = "./prompts"):
        self.dir = Path(prompts_dir)
        self._cache = {}

    def get(self, name: str) -> Prompt:
        if name not in self._cache:
            self._cache[name] = load_prompt(name)
        return self._cache[name]

    def get_version(self, name: str) -> str:
        prompt = self.get(name)
        return prompt.version

    def get_hash(self, name: str) -> str:
        prompt = self.get(name)
        content = f"{prompt.system}{prompt.user_template}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

registry = PromptRegistry()
```

---

## 6. CI/CD for Prompts

### GitHub Action

```yaml
# .github/workflows/prompt-tests.yml
name: Prompt Tests

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'tests/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run prompt tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python -m pytest tests/prompts/ -v
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: prompt-lint
        name: Prompt Lint
        entry: python scripts/lint_prompts.py
        language: python
        files: prompts/.*\.yaml$
```

---

## Quick Reference

### Load Prompt

```python
prompt = load_prompt("summarize")
messages = render_prompt(prompt, text="...")
```

### Run Tests

```python
results = run_prompt_tests(prompt, "tests/summarize.yaml", llm_call)
```

### A/B Test

```python
prompt, variant = get_prompt("experiment_name", user_id)
```

---

## Summary

You've learned:

1. **Versioning** — Prompts as YAML config
2. **Regression testing** — Assertions on outputs
3. **A/B testing** — Compare prompt variants
4. **Registries** — Centralized prompt management
5. **CI/CD** — Automated prompt testing

**Month 5 Complete!** You can now build observable, evaluated AI systems.
