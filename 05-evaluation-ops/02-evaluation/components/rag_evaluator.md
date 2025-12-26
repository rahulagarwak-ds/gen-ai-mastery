# Mini Project: RAG Evaluator

## 🎯 Objective

Build an automated evaluation pipeline for RAG systems.

---

## 📋 Requirements

### 1. Test Case Format

```python
from dataclasses import dataclass

@dataclass
class RAGTestCase:
    id: str
    query: str
    expected_answer: str
    relevant_doc_ids: list[str] = None
    tags: list[str] = None

def load_test_cases(path: str) -> list[RAGTestCase]:
    """Load test cases from YAML."""
    pass
```

### 2. Metrics

```python
class RAGMetrics:
    @staticmethod
    def answer_similarity(
        actual: str,
        expected: str
    ) -> float:
        """Semantic similarity 0-1."""
        pass

    @staticmethod
    def retrieval_precision(
        retrieved: list[str],
        relevant: list[str],
        k: int = 5
    ) -> float:
        """Precision@K."""
        pass

    @staticmethod
    def faithfulness(
        answer: str,
        context: list[str]
    ) -> float:
        """LLM-as-judge for groundedness."""
        pass
```

### 3. Evaluator

```python
@dataclass
class EvalResult:
    test_id: str
    passed: bool
    answer_score: float
    retrieval_score: float
    faithfulness_score: float

class RAGEvaluator:
    def __init__(self, rag_fn, pass_threshold: float = 0.8):
        self.rag_fn = rag_fn
        self.threshold = pass_threshold

    def evaluate(self, case: RAGTestCase) -> EvalResult:
        pass

    def run_suite(self, cases: list[RAGTestCase]) -> dict:
        """Return aggregate metrics."""
        pass
```

---

## ✅ Test Cases

```python
evaluator = RAGEvaluator(my_rag_pipeline)

# Single case
result = evaluator.evaluate(RAGTestCase(
    id="test_1",
    query="What is Python?",
    expected_answer="Python is a programming language."
))
assert result.answer_score >= 0

# Suite
suite_results = evaluator.run_suite(load_test_cases("tests.yaml"))
print(f"Pass rate: {suite_results['pass_rate']:.1%}")
```

**Time estimate:** 3-4 hours
