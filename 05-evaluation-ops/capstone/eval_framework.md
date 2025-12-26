# 🏆 Month 5 Capstone: Eval Framework

## 🎯 Objective

Build an automated evaluation framework for your RAG system that:

- Runs test suites on prompts
- Evaluates retrieval quality
- Measures response accuracy
- Tracks metrics over time

---

## 📋 Requirements

### 1. Test Case Format

```python
@dataclass
class EvalCase:
    id: str
    query: str
    expected_answer: str
    expected_sources: list[str] = None
    tags: list[str] = None

# Load from YAML
eval_cases = load_eval_dataset("evals/rag_tests.yaml")
```

### 2. Evaluator Interface

```python
class RAGEvaluator:
    def __init__(self, rag_pipeline, judge_model: str = "gpt-4o"):
        pass

    def evaluate_single(self, case: EvalCase) -> EvalResult:
        """Run single evaluation."""
        pass

    def evaluate_suite(self, cases: list[EvalCase]) -> SuiteResult:
        """Run all cases and aggregate."""
        pass

    def compare_pipelines(
        self,
        cases: list[EvalCase],
        pipelines: dict[str, Callable]
    ) -> ComparisonResult:
        """A/B compare multiple pipelines."""
        pass

@dataclass
class EvalResult:
    case_id: str
    answer: str
    sources: list[str]
    metrics: dict  # relevance, faithfulness, accuracy
    passed: bool

@dataclass
class SuiteResult:
    total: int
    passed: int
    failed: int
    avg_metrics: dict
    failures: list[EvalResult]
```

### 3. Metrics

- **Answer Accuracy**: LLM-as-judge score (1-5)
- **Context Relevance**: Retrieved docs match query
- **Faithfulness**: Response grounded in context
- **Retrieval Precision**: Relevant docs in top-k

### 4. CLI Interface

```bash
# Run evaluation
eval-framework run --suite evals/rag_tests.yaml --output results.json

# Compare two prompts
eval-framework compare --baseline v1.yaml --candidate v2.yaml

# Generate report
eval-framework report --input results.json --format markdown
```

---

## 📁 Project Structure

```
eval_framework/
├── __init__.py
├── models.py          # EvalCase, EvalResult, etc.
├── evaluator.py       # RAGEvaluator
├── metrics/
│   ├── accuracy.py    # LLM-as-judge
│   ├── retrieval.py   # Precision, recall, MRR
│   └── faithfulness.py
├── loaders.py         # Load YAML test cases
├── reporters.py       # Generate reports
└── cli.py

evals/
├── rag_tests.yaml
└── edge_cases.yaml
```

---

## ✅ Test Cases

```python
evaluator = RAGEvaluator(my_rag_pipeline)

# Single evaluation
result = evaluator.evaluate_single(EvalCase(
    id="test_1",
    query="What is Python?",
    expected_answer="A programming language"
))
assert result.metrics["accuracy"] >= 0.8

# Suite evaluation
suite = evaluator.evaluate_suite(load_cases("evals/rag_tests.yaml"))
assert suite.passed / suite.total >= 0.9  # 90% pass rate

# Pipeline comparison
comparison = evaluator.compare_pipelines(
    cases,
    {"v1": pipeline_v1, "v2": pipeline_v2}
)
print(f"Winner: {comparison.winner}")
```

---

## 🏆 Bonus

1. **Regression Detection**: Alert on performance drops
2. **GitHub Action**: Run evals on PR
3. **Dashboard**: Visualize metrics over time
4. **Cost Tracking**: Monitor eval costs

**Time estimate:** 4-6 hours
