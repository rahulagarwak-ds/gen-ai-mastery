# Mini Project: Optimized Retriever

## 🎯 Objective

Build a production-ready retriever with hybrid search, reranking, and caching.

---

## 📋 Requirements

### 1. Hybrid Retriever

```python
from dataclasses import dataclass
import numpy as np

@dataclass
class RetrievalResult:
    doc_id: str
    content: str
    score: float
    source: str  # "dense", "sparse", or "hybrid"

class HybridRetriever:
    def __init__(
        self,
        documents: list[str],
        doc_ids: list[str],
        embed_fn
    ):
        # Pre-compute embeddings
        # Build BM25 index
        pass

    def search(
        self,
        query: str,
        k: int = 10,
        alpha: float = 0.5
    ) -> list[RetrievalResult]:
        """Hybrid search with score fusion."""
        pass
```

### 2. Reranker Wrapper

```python
class Reranker:
    def __init__(self, model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        pass

    def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 5
    ) -> list[RetrievalResult]:
        pass
```

### 3. Cached Retriever

```python
class CachedRetriever:
    def __init__(
        self,
        retriever: HybridRetriever,
        reranker: Reranker = None,
        cache_threshold: float = 0.95
    ):
        pass

    def search(self, query: str, k: int = 5) -> list[RetrievalResult]:
        """
        1. Check semantic cache
        2. If miss: retrieve → rerank → cache
        3. Return results
        """
        pass

    def get_cache_stats(self) -> dict:
        """Return hit rate, size, etc."""
        pass
```

---

## ✅ Test Cases

```python
# Setup
docs = ["Python is...", "JavaScript runs...", ...]
retriever = HybridRetriever(docs, range(len(docs)), embed_fn)
reranker = Reranker()
cached = CachedRetriever(retriever, reranker)

# Hybrid search
results = retriever.search("Python programming", k=5, alpha=0.7)
assert len(results) == 5
assert all(r.score >= 0 for r in results)

# Reranking
reranked = reranker.rerank("Python", results, top_k=3)
assert len(reranked) == 3

# Caching
r1 = cached.search("What is Python?")
r2 = cached.search("What's Python?")  # Should hit cache
stats = cached.get_cache_stats()
assert stats["hit_rate"] > 0
```

---

## 🎁 Bonus

1. Add query expansion before retrieval
2. Implement async batch retrieval
3. Add latency tracking per component

**Time estimate:** 4-5 hours
