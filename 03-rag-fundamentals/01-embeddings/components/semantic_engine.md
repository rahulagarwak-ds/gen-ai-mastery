# Mini Project: Semantic Search Engine

## 🎯 Objective

Build a reusable semantic search engine that can be used as a foundation for RAG systems.

---

## 📋 Requirements

### 1. Core Classes

```python
from dataclasses import dataclass
from typing import Callable, Literal
import numpy as np

@dataclass
class SearchResult:
    content: str
    score: float
    metadata: dict
    index: int

class SemanticEngine:
    def __init__(
        self,
        embedding_model: Literal["openai", "sentence-transformers"] = "sentence-transformers",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        pass

    def add(self, documents: list[str], metadatas: list[dict] = None):
        """Add documents to the index."""
        pass

    def search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.0
    ) -> list[SearchResult]:
        """Search for similar documents."""
        pass

    def search_batch(
        self,
        queries: list[str],
        k: int = 5
    ) -> list[list[SearchResult]]:
        """Search multiple queries efficiently."""
        pass

    def save(self, path: str):
        """Save index to disk."""
        pass

    @classmethod
    def load(cls, path: str) -> "SemanticEngine":
        """Load index from disk."""
        pass
```

### 2. Features

**Multiple Embedding Backends:**

```python
# Sentence Transformers (local)
engine = SemanticEngine(embedding_model="sentence-transformers")

# OpenAI (API)
engine = SemanticEngine(embedding_model="openai", model_name="text-embedding-3-small")
```

**Metadata Filtering:**

```python
results = engine.search(
    "machine learning",
    k=5,
    filter={"category": "tech", "year": {"$gte": 2023}}
)
```

**Incremental Indexing:**

```python
engine.add(["doc1", "doc2"])
engine.add(["doc3", "doc4"])  # Adds to existing index
```

**Persistence:**

```python
engine.save("./my_index")
engine = SemanticEngine.load("./my_index")
```

---

## 📁 Project Structure

```
semantic_engine/
├── __init__.py
├── engine.py           # Main SemanticEngine class
├── embeddings/
│   ├── base.py         # Abstract embedder
│   ├── openai.py       # OpenAI embeddings
│   └── local.py        # Sentence Transformers
├── similarity.py       # Cosine, dot product, euclidean
└── storage.py          # Save/load functionality
```

---

## ✅ Test Cases

```python
from semantic_engine import SemanticEngine

# Basic usage
engine = SemanticEngine()
engine.add([
    "Python is a programming language",
    "JavaScript runs in browsers",
    "Machine learning uses algorithms"
])

results = engine.search("AI and neural networks", k=2)
assert len(results) == 2
assert "machine learning" in results[0].content.lower()

# Persistence
engine.save("./test_index")
loaded = SemanticEngine.load("./test_index")
results2 = loaded.search("AI", k=1)
assert results2[0].content == results[0].content

# Batch search
batch_results = engine.search_batch(["Python", "JavaScript"], k=1)
assert len(batch_results) == 2
```

---

## 🏆 Bonus

1. Add FAISS backend for large-scale search
2. Add approximate nearest neighbors (HNSW)
3. Add query caching
4. Add embedding caching

**Time estimate:** 2-3 hours
