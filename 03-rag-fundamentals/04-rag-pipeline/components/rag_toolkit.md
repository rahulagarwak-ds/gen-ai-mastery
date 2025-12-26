# Mini Project: RAG Toolkit

## 🎯 Objective

Build a modular RAG toolkit with pluggable components for retrieval, reranking, and generation.

---

## 📋 Requirements

### 1. Modular Architecture

```python
from abc import ABC, abstractmethod

# Retriever interface
class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        pass

# Reranker interface
class Reranker(ABC):
    @abstractmethod
    def rerank(self, query: str, docs: list[dict], k: int = 5) -> list[dict]:
        pass

# Generator interface
class Generator(ABC):
    @abstractmethod
    def generate(self, query: str, context: list[dict]) -> str:
        pass
```

### 2. Implementations

**Retrievers:**

```python
class ChromaRetriever(Retriever):
    """Uses ChromaDB for retrieval."""
    pass

class HybridRetriever(Retriever):
    """Combines semantic + keyword search."""
    pass
```

**Rerankers:**

```python
class CrossEncoderReranker(Reranker):
    """Uses cross-encoder model."""
    pass

class NoopReranker(Reranker):
    """Pass-through, no reranking."""
    pass
```

**Generators:**

```python
class OpenAIGenerator(Generator):
    """Uses OpenAI for generation."""
    pass

class StreamingGenerator(Generator):
    """Streams response tokens."""
    pass
```

### 3. RAG Pipeline Builder

```python
class RAGPipeline:
    def __init__(
        self,
        retriever: Retriever,
        generator: Generator,
        reranker: Reranker = None
    ):
        self.retriever = retriever
        self.generator = generator
        self.reranker = reranker or NoopReranker()

    def query(self, question: str, k: int = 5) -> dict:
        # Retrieve
        docs = self.retriever.retrieve(question, k=k * 2 if self.reranker else k)

        # Rerank
        docs = self.reranker.rerank(question, docs, k=k)

        # Generate
        answer = self.generator.generate(question, docs)

        return {
            "answer": answer,
            "sources": docs,
            "query": question
        }

# Usage
pipeline = RAGPipeline(
    retriever=ChromaRetriever(collection),
    reranker=CrossEncoderReranker(),
    generator=OpenAIGenerator()
)

result = pipeline.query("What is Python?")
```

---

## 📁 Project Structure

```
rag_toolkit/
├── __init__.py
├── retrieval/
│   ├── base.py
│   ├── chroma.py
│   └── hybrid.py
├── reranking/
│   ├── base.py
│   └── cross_encoder.py
├── generation/
│   ├── base.py
│   └── openai.py
├── pipeline.py
└── presets.py          # Pre-configured pipelines
```

---

## ✅ Test Cases

```python
from rag_toolkit import RAGPipeline, ChromaRetriever, OpenAIGenerator

# Basic pipeline
retriever = ChromaRetriever.from_documents([
    "Python is a programming language",
    "JavaScript runs in browsers"
])
generator = OpenAIGenerator()

pipeline = RAGPipeline(retriever, generator)
result = pipeline.query("What is Python?")

assert "Python" in result["answer"]
assert len(result["sources"]) > 0

# With reranker
from rag_toolkit import CrossEncoderReranker

pipeline_v2 = RAGPipeline(
    retriever, generator,
    reranker=CrossEncoderReranker()
)
result2 = pipeline_v2.query("What is Python?")
```

---

## 🏆 Bonus

1. Add evaluation module (hit rate, MRR)
2. Add query expansion component
3. Add caching layer
4. Add async pipeline

**Time estimate:** 3-4 hours
