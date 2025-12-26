# Chapter 2: Evaluation — Measuring AI Quality

> _"If you can't measure it, you can't improve it."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Types of LLM evaluation
- Automated evaluation metrics
- LLM-as-judge patterns
- RAG evaluation (retrieval + generation)
- Building evaluation datasets

---

## 1. Types of Evaluation

### The Evaluation Pyramid

```
                    ┌─────────────┐
                    │   Human     │  Gold standard, expensive
                    │   Eval      │
                    ├─────────────┤
                    │  LLM-as-    │  Scalable, good correlation
                    │   Judge     │
                    ├─────────────┤
                    │  Heuristic  │  Fast, limited scope
                    │   Metrics   │
                    └─────────────┘
```

### When to Use Each

| Method       | Use Case                     | Cost |
| ------------ | ---------------------------- | ---- |
| Human        | Final validation, edge cases | $$$  |
| LLM-as-Judge | Development, CI/CD           | $$   |
| Heuristics   | Quick checks, filtering      | $    |

---

## 2. Heuristic Metrics

### Basic Checks

````python
def evaluate_response(response: str) -> dict:
    """Quick heuristic checks."""
    return {
        "length": len(response),
        "word_count": len(response.split()),
        "has_code": "```" in response,
        "is_refusal": any(phrase in response.lower() for phrase in [
            "i cannot", "i can't", "i'm unable to"
        ]),
        "contains_json": response.strip().startswith("{"),
    }
````

### Text Similarity

```python
from difflib import SequenceMatcher

def similarity(a: str, b: str) -> float:
    """Calculate string similarity (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# For semantic similarity, use embeddings
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_similarity(a: str, b: str) -> float:
    embeddings = model.encode([a, b])
    return float(np.dot(embeddings[0], embeddings[1]))
```

---

## 3. LLM-as-Judge

### Basic Evaluator

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class EvalResult(BaseModel):
    score: int  # 1-5
    reasoning: str

def evaluate_with_llm(
    query: str,
    response: str,
    criteria: str
) -> EvalResult:
    """Use LLM to evaluate a response."""

    prompt = f"""Evaluate the following response.

Query: {query}
Response: {response}

Criteria: {criteria}

Rate from 1-5 where:
1 = Completely wrong/irrelevant
3 = Partially correct
5 = Perfect response

Return JSON with "score" and "reasoning" fields."""

    result = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return EvalResult.model_validate_json(result.choices[0].message.content)
```

### Multi-Criteria Evaluation

```python
CRITERIA = {
    "relevance": "Is the response relevant to the query?",
    "accuracy": "Is the information factually correct?",
    "completeness": "Does it fully answer the question?",
    "clarity": "Is the response clear and well-organized?",
}

def multi_criteria_eval(query: str, response: str) -> dict[str, EvalResult]:
    return {
        name: evaluate_with_llm(query, response, description)
        for name, description in CRITERIA.items()
    }
```

### Pairwise Comparison

```python
def compare_responses(
    query: str,
    response_a: str,
    response_b: str
) -> str:
    """Compare two responses, return winner ("A", "B", or "tie")."""

    prompt = f"""Compare these two responses to the query.

Query: {query}

Response A:
{response_a}

Response B:
{response_b}

Which response is better? Answer with only: A, B, or tie"""

    result = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return result.choices[0].message.content.strip()
```

---

## 4. RAG Evaluation

### Retrieval Metrics

```python
def retrieval_metrics(
    retrieved: list[str],
    relevant: list[str],
    k: int = 5
) -> dict:
    """Calculate retrieval quality metrics."""

    retrieved_set = set(retrieved[:k])
    relevant_set = set(relevant)

    # Precision: What % of retrieved is relevant?
    precision = len(retrieved_set & relevant_set) / len(retrieved_set) if retrieved_set else 0

    # Recall: What % of relevant was retrieved?
    recall = len(retrieved_set & relevant_set) / len(relevant_set) if relevant_set else 0

    # Hit Rate: Did we find at least one relevant?
    hit = len(retrieved_set & relevant_set) > 0

    # MRR: Reciprocal rank of first relevant
    mrr = 0
    for i, doc in enumerate(retrieved):
        if doc in relevant_set:
            mrr = 1 / (i + 1)
            break

    return {
        "precision@k": precision,
        "recall@k": recall,
        "hit_rate": hit,
        "mrr": mrr,
    }
```

### Context Relevance

```python
def evaluate_context_relevance(
    query: str,
    context: list[str]
) -> float:
    """Score how relevant retrieved context is to query."""

    prompt = f"""Rate the relevance of this context to the query.

Query: {query}

Context:
{chr(10).join(context)}

Score from 0.0 to 1.0 where 1.0 = perfectly relevant.
Return only the number."""

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return float(result.choices[0].message.content.strip())
```

### Faithfulness (Groundedness)

```python
def evaluate_faithfulness(
    response: str,
    context: list[str]
) -> float:
    """Score if response is grounded in context (no hallucination)."""

    prompt = f"""Evaluate if the response is fully supported by the context.

Context:
{chr(10).join(context)}

Response:
{response}

Score from 0.0 to 1.0 where:
0.0 = Response contains claims not in context
1.0 = Everything in response is supported by context

Return only the number."""

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return float(result.choices[0].message.content.strip())
```

---

## 5. Evaluation Datasets

### Creating Test Cases

```python
from dataclasses import dataclass

@dataclass
class TestCase:
    id: str
    query: str
    expected_answer: str
    context: list[str] = None
    tags: list[str] = None

test_cases = [
    TestCase(
        id="capital_france",
        query="What is the capital of France?",
        expected_answer="Paris",
        tags=["geography", "factual"]
    ),
    TestCase(
        id="python_creator",
        query="Who created Python?",
        expected_answer="Guido van Rossum",
        tags=["tech", "history"]
    ),
]
```

### Running Evaluation Suite

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class EvalResult:
    test_id: str
    passed: bool
    score: float
    details: dict

def run_eval_suite(
    test_cases: list[TestCase],
    pipeline: Callable[[str], str],  # query -> response
    evaluator: Callable[[str, str, str], float]  # query, response, expected -> score
) -> list[EvalResult]:
    """Run all test cases through pipeline and evaluate."""

    results = []
    for case in test_cases:
        response = pipeline(case.query)
        score = evaluator(case.query, response, case.expected_answer)

        results.append(EvalResult(
            test_id=case.id,
            passed=score >= 0.8,
            score=score,
            details={
                "query": case.query,
                "expected": case.expected_answer,
                "actual": response
            }
        ))

    return results

def print_results(results: list[EvalResult]):
    passed = sum(1 for r in results if r.passed)
    print(f"\nResults: {passed}/{len(results)} passed")
    print(f"Average score: {sum(r.score for r in results)/len(results):.2f}")

    for r in results:
        status = "✅" if r.passed else "❌"
        print(f"  {status} {r.test_id}: {r.score:.2f}")
```

---

## 6. RAGAS Framework

### Setup

```bash
uv add ragas
```

### Built-in Metrics

```python
from ragas import evaluate
from ragas.metrics import (
    context_relevancy,
    faithfulness,
    answer_relevancy,
    context_precision
)
from datasets import Dataset

# Prepare data
data = {
    "question": ["What is Python?"],
    "answer": ["Python is a programming language."],
    "contexts": [["Python is a high-level programming language..."]],
    "ground_truth": ["Python is a programming language."]
}

dataset = Dataset.from_dict(data)

# Evaluate
result = evaluate(
    dataset,
    metrics=[
        context_relevancy,
        faithfulness,
        answer_relevancy,
    ]
)

print(result)
```

---

## Quick Reference

### Heuristic

```python
similarity = SequenceMatcher(None, a, b).ratio()
```

### LLM-as-Judge

```python
score = evaluate_with_llm(query, response, criteria)
```

### RAG Metrics

```python
metrics = retrieval_metrics(retrieved, relevant, k=5)
faithfulness = evaluate_faithfulness(response, context)
```

---

## Summary

You've learned:

1. **Evaluation types** — Human, LLM, heuristic
2. **Heuristic metrics** — Quick checks, similarity
3. **LLM-as-Judge** — Scalable evaluation
4. **RAG evaluation** — Retrieval + faithfulness
5. **Test suites** — Structured evaluation

Next chapter: Prompt Testing — Version control and regression.
