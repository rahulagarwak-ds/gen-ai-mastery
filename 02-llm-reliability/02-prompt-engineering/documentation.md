# Chapter 2: Prompt Engineering — The Art of Instruction

> _"A good prompt is worth a thousand fine-tuning runs."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- The anatomy of effective prompts
- Prompt templates and variable injection
- Few-shot learning (teaching by example)
- Chain of Thought (CoT) reasoning
- Role prompting and personas
- Common prompt patterns and anti-patterns

---

## 1. The Anatomy of a Prompt

### Basic Structure

```
┌─────────────────────────────────────┐
│ SYSTEM PROMPT (optional)            │
│ - Role definition                   │
│ - Rules and constraints             │
│ - Output format                     │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ CONTEXT (optional)                  │
│ - Background information            │
│ - Relevant data                     │
│ - Examples (few-shot)               │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ INSTRUCTION                         │
│ - Clear task description            │
│ - Specific requirements             │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ INPUT                               │
│ - User data to process              │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ OUTPUT SPECIFICATION (optional)     │
│ - Expected format                   │
│ - Examples of desired output        │
└─────────────────────────────────────┘
```

### Example: Bad vs Good Prompt

```python
# ❌ Bad: Vague, no structure
bad_prompt = "Summarize this article"

# ✅ Good: Clear, structured, specific
good_prompt = """
Summarize the following article in exactly 3 bullet points.
Each bullet should be one sentence, maximum 20 words.
Focus on the main argument, key evidence, and conclusion.

Article:
{article_text}

Summary:
"""
```

---

## 2. Prompt Templates

### Why Templates?

Templates separate **logic** from **content**:

```python
# Without template (hardcoded)
prompt = "Translate 'hello' to Spanish"

# With template (reusable)
template = "Translate '{text}' to {language}"
prompt = template.format(text="hello", language="Spanish")
```

### Simple Template Pattern

```python
from string import Template

class PromptTemplate:
    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

    @property
    def variables(self) -> list[str]:
        import re
        return re.findall(r'\{(\w+)\}', self.template)

# Usage
summarize = PromptTemplate("""
Summarize the following text in {num_sentences} sentences.

Text: {text}

Summary:
""")

prompt = summarize.format(
    num_sentences=3,
    text="Python is a programming language..."
)
```

### Production Pattern: Dataclass Templates

```python
from dataclasses import dataclass

@dataclass
class SummaryPrompt:
    text: str
    num_sentences: int = 3
    style: str = "concise"

    def build(self) -> list[dict]:
        return [
            {
                "role": "system",
                "content": f"You are a {self.style} summarizer."
            },
            {
                "role": "user",
                "content": f"""
Summarize in exactly {self.num_sentences} sentences:

{self.text}
"""
            }
        ]

# Usage
prompt = SummaryPrompt(
    text="Long article here...",
    num_sentences=5,
    style="academic"
)
messages = prompt.build()
```

---

## 3. Few-Shot Learning

### What is Few-Shot?

Teach the model by showing examples instead of explaining:

```
Zero-shot:  No examples, just instruction
One-shot:   1 example
Few-shot:   2-5 examples
Many-shot:  6+ examples
```

### Zero-Shot vs Few-Shot

```python
# Zero-shot: Just instruction
zero_shot = """
Classify the sentiment as positive, negative, or neutral.

Text: "This product is terrible!"
Sentiment:
"""

# Few-shot: Examples first
few_shot = """
Classify the sentiment as positive, negative, or neutral.

Text: "I love this product!"
Sentiment: positive

Text: "It's okay, nothing special."
Sentiment: neutral

Text: "Worst purchase ever."
Sentiment: negative

Text: "This product is terrible!"
Sentiment:
"""
```

### Few-Shot Best Practices

```python
def build_few_shot_prompt(
    examples: list[dict],
    query: str,
    instruction: str
) -> str:
    prompt_parts = [instruction, ""]

    for ex in examples:
        prompt_parts.append(f"Input: {ex['input']}")
        prompt_parts.append(f"Output: {ex['output']}")
        prompt_parts.append("")

    prompt_parts.append(f"Input: {query}")
    prompt_parts.append("Output:")

    return "\n".join(prompt_parts)

# Usage
examples = [
    {"input": "The food was delicious!", "output": "positive"},
    {"input": "Service was slow and rude.", "output": "negative"},
    {"input": "It was an average experience.", "output": "neutral"},
]

prompt = build_few_shot_prompt(
    examples=examples,
    query="Best restaurant I've ever been to!",
    instruction="Classify the sentiment as positive, negative, or neutral."
)
```

### Selecting Good Examples

| ✅ Do                     | ❌ Don't                 |
| ------------------------- | ------------------------ |
| Cover edge cases          | Use only easy examples   |
| Show variety              | Repeat similar patterns  |
| Match target distribution | Over-represent one class |
| Use realistic data        | Use toy examples         |

---

## 4. Chain of Thought (CoT)

### What is CoT?

Force the model to "think step by step" before answering:

```python
# Without CoT
prompt = "What is 17 * 23?"
# Model might guess incorrectly

# With CoT
prompt = """
What is 17 * 23?

Let's solve this step by step:
"""
# Model reasons through the calculation
```

### Zero-Shot CoT

Just add the magic phrase:

```python
prompt = """
Question: If a train travels at 60 mph for 2.5 hours,
how far does it travel?

Let's think step by step:
"""
```

### Few-Shot CoT

Show examples of reasoning:

```python
cot_examples = """
Question: If a store has 15 apples and sells 7, how many are left?
Let's think step by step:
1. Start with 15 apples
2. Subtract the sold apples: 15 - 7 = 8
3. Therefore, 8 apples are left.
Answer: 8

Question: A book costs $12 and is on 25% sale. What's the sale price?
Let's think step by step:
1. Calculate the discount: $12 * 0.25 = $3
2. Subtract from original: $12 - $3 = $9
3. Therefore, the sale price is $9.
Answer: $9

Question: {user_question}
Let's think step by step:
"""
```

### When to Use CoT

| Use CoT              | Don't Use CoT         |
| -------------------- | --------------------- |
| Math problems        | Simple classification |
| Multi-step reasoning | Factual recall        |
| Logic puzzles        | Translation           |
| Planning tasks       | Summarization         |

---

## 5. Role Prompting

### Why Roles Matter

Roles prime the model's knowledge and style:

```python
# Generic
response = llm.chat([
    {"role": "user", "content": "Review this code for bugs"}
])

# With role
response = llm.chat([
    {"role": "system", "content": """
    You are a senior Python developer with 15 years of experience.
    You specialize in finding subtle bugs and security vulnerabilities.
    Be thorough but concise.
    """},
    {"role": "user", "content": "Review this code for bugs: ..."}
])
```

### Effective Role Templates

```python
EXPERT_ROLE = """
You are an expert {domain} specialist with {years} years of experience.

Your expertise includes:
{expertise_list}

Communication style:
- {style_trait_1}
- {style_trait_2}
"""

# Example
code_reviewer = EXPERT_ROLE.format(
    domain="Python backend",
    years="15",
    expertise_list="- Clean code principles\n- Security best practices\n- Performance optimization",
    style_trait_1="Be direct and specific",
    style_trait_2="Prioritize critical issues first"
)
```

### Persona Library

```python
PERSONAS = {
    "code_reviewer": """
        You are a meticulous senior software engineer.
        You focus on: bugs, security, performance, maintainability.
        Be constructive, not critical.
    """,

    "explainer": """
        You are a patient teacher who explains complex topics simply.
        Use analogies and examples.
        Avoid jargon unless defining it first.
    """,

    "analyst": """
        You are a data analyst who thinks in numbers and evidence.
        Always cite sources or express uncertainty.
        Use bullet points for clarity.
    """,

    "editor": """
        You are a professional editor and writer.
        Focus on: clarity, conciseness, grammar, flow.
        Preserve the author's voice while improving quality.
    """
}
```

---

## 6. Prompt Patterns

### The CRISP Framework

```
C - Context:    Background information
R - Role:       Who the AI should be
I - Instruction: What to do
S - Specifics:   Constraints and details
P - Prompt:      The actual input
```

```python
CRISP_PROMPT = """
[CONTEXT]
You are helping a user understand their electricity bill.
The user is not technical and needs simple explanations.

[ROLE]
You are a friendly customer service representative for an electric company.

[INSTRUCTION]
Explain the charges on the bill in simple terms.
Identify any unusual charges or potential savings.

[SPECIFICS]
- Use everyday language, no jargon
- Keep explanations under 2 sentences each
- Highlight the total amount due

[INPUT]
{bill_text}
"""
```

### The Instruction → Example → Input Pattern

```python
PATTERN = """
INSTRUCTION:
{instruction}

EXAMPLES:
{examples}

INPUT:
{user_input}

OUTPUT:
"""
```

### The Structured Output Pattern

```python
STRUCTURED = """
Analyze the following customer feedback and extract:
1. Sentiment (positive/negative/neutral)
2. Main topic (one or two words)
3. Key issues (list of 1-3 issues)
4. Suggested action (one sentence)

Respond in exactly this format:
Sentiment: [value]
Topic: [value]
Issues: [value1], [value2]
Action: [value]

Feedback: {feedback}
"""
```

---

## 7. Common Anti-Patterns

### ❌ Too Vague

```python
# Bad
"Help me with my email"

# Good
"Rewrite this email to be more professional and concise.
Keep the main request but remove filler phrases.

Email: {email_text}"
```

### ❌ Too Long

```python
# Bad: 500-word instruction
"When you read this text, I want you to carefully consider all the
nuances and implications of what the author is trying to say, taking
into account the historical context, the cultural background, the
intended audience... [continues for paragraphs]"

# Good: Concise
"Summarize the main argument in 2 sentences. Include historical context."
```

### ❌ Conflicting Instructions

```python
# Bad
"Be creative and generate novel ideas, but stick strictly to the facts."

# Good
"Generate 3 creative marketing slogans based on these product features: ..."
```

### ❌ Assuming Context

```python
# Bad
"Based on our previous conversation, what should I do?"

# Good
"Context: I'm launching a mobile app for fitness tracking.
Question: What are 3 effective marketing channels for this type of app?"
```

---

## 8. Prompt Testing

### A/B Testing Prompts

```python
from dataclasses import dataclass
from typing import Callable
import random

@dataclass
class PromptVariant:
    name: str
    template: str

def test_prompts(
    variants: list[PromptVariant],
    test_inputs: list[str],
    evaluator: Callable[[str, str], float]  # input, output -> score
) -> dict:
    results = {}

    for variant in variants:
        scores = []
        for input_text in test_inputs:
            prompt = variant.template.format(input=input_text)
            output = llm.chat([{"role": "user", "content": prompt}])
            score = evaluator(input_text, output)
            scores.append(score)

        results[variant.name] = {
            "mean": sum(scores) / len(scores),
            "scores": scores
        }

    return results
```

### Prompt Versioning

```python
PROMPT_REGISTRY = {
    "summarize_v1": "Summarize this: {text}",
    "summarize_v2": "Summarize in 3 bullets: {text}",
    "summarize_v3": "As an expert editor, summarize key points: {text}",
}

def get_prompt(name: str, version: str = "latest") -> str:
    key = f"{name}_{version}" if version != "latest" else max(
        k for k in PROMPT_REGISTRY if k.startswith(name)
    )
    return PROMPT_REGISTRY[key]
```

---

## Quick Reference

### Prompt Structure

```
System: [Role + Rules]
Context: [Background + Examples]
Instruction: [Clear task]
Input: [User data]
Format: [Expected output]
```

### Key Techniques

| Technique | When to Use                |
| --------- | -------------------------- |
| Few-shot  | Classification, formatting |
| CoT       | Reasoning, math, logic     |
| Role      | Expertise, style control   |
| Templates | Reusable prompts           |

### Magic Phrases

- "Let's think step by step"
- "Explain your reasoning"
- "List exactly N items"
- "Respond in exactly this format:"

---

## Summary

You've learned:

1. **Prompt anatomy** — system, context, instruction, input, output
2. **Templates** — reusable, parameterized prompts
3. **Few-shot** — teaching by example
4. **Chain of Thought** — step-by-step reasoning
5. **Role prompting** — personas and expertise
6. **Patterns** — CRISP, structured output
7. **Anti-patterns** — what to avoid
8. **Testing** — A/B testing, versioning

Next chapter: Structured Outputs — forcing valid, parseable responses.
