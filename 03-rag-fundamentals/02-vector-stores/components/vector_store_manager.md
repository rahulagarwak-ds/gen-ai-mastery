# Mini Project: Vector Store Manager

## 🎯 Objective

Build a unified vector store interface that abstracts multiple backends (ChromaDB, in-memory, file-based).

---

## 📋 Requirements

### 1. Abstract Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Document:
    id: str
    content: str
    embedding: list[float] | None = None
    metadata: dict = None

@dataclass
class QueryResult:
    document: Document
    score: float

class VectorStore(ABC):
    @abstractmethod
    def add(self, documents: list[Document]) -> list[str]:
        """Add documents, return IDs."""
        pass

    @abstractmethod
    def query(
        self,
        embedding: list[float],
        k: int = 5,
        filter: dict = None
    ) -> list[QueryResult]:
        """Query by embedding."""
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> int:
        """Delete by IDs, return count deleted."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total document count."""
        pass
```

### 2. Implementations

**In-Memory (for testing):**

```python
class InMemoryStore(VectorStore):
    """Fast, no dependencies, ephemeral."""
    pass
```

**File-Based (simple persistence):**

```python
class FileStore(VectorStore):
    """JSON-based storage, good for small datasets."""
    def __init__(self, path: str):
        pass
```

**ChromaDB (production):**

```python
class ChromaStore(VectorStore):
    """Full-featured vector DB."""
    def __init__(self, collection_name: str, persist_dir: str = None):
        pass
```

### 3. Factory Pattern

```python
def create_store(
    backend: str = "memory",
    **kwargs
) -> VectorStore:
    """Create a vector store by backend name."""
    backends = {
        "memory": InMemoryStore,
        "file": FileStore,
        "chroma": ChromaStore,
    }
    return backends[backend](**kwargs)

# Usage
store = create_store("chroma", collection_name="docs", persist_dir="./data")
```

---

## 📁 Project Structure

```
vector_store/
├── __init__.py
├── base.py             # Abstract VectorStore
├── memory.py           # InMemoryStore
├── file.py             # FileStore
├── chroma.py           # ChromaStore
└── factory.py          # create_store function
```

---

## ✅ Test Cases

```python
from vector_store import create_store, Document

# Test all backends
for backend in ["memory", "file", "chroma"]:
    store = create_store(backend, path="./test" if backend == "file" else None)

    # Add
    docs = [
        Document(id="1", content="Hello", embedding=[0.1]*384),
        Document(id="2", content="World", embedding=[0.2]*384),
    ]
    ids = store.add(docs)
    assert len(ids) == 2

    # Count
    assert store.count() == 2

    # Query
    results = store.query([0.1]*384, k=1)
    assert len(results) == 1
    assert results[0].document.id == "1"

    # Delete
    deleted = store.delete(["1"])
    assert deleted == 1
    assert store.count() == 1
```

---

## 🏆 Bonus

1. Add Pinecone backend
2. Add pgvector backend
3. Add batch operations with progress bar
4. Add automatic embedding generation

**Time estimate:** 2-3 hours
