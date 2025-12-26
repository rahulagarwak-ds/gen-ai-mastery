# Chapter 1: Embeddings — Meaning as Numbers

> _"Embeddings let computers understand meaning, not just match words."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- What embeddings are and why they matter
- How text becomes vectors
- Different embedding models and when to use them
- Similarity metrics (cosine, dot product, euclidean)
- OpenAI and open-source embedding options
- Practical embedding patterns

---

## 1. What Are Embeddings?

### The Problem

Computers don't understand meaning:

```python
# To a computer, these are completely different
"I love Python"
"Python is my favorite"

# Even though they mean nearly the same thing
```

### The Solution: Embeddings

Embeddings convert text to vectors (lists of numbers) where **similar meanings are close together**:

```python
# Each text becomes a vector
"I love Python"         → [0.12, -0.34, 0.56, ..., 0.78]  # 1536 numbers
"Python is my favorite" → [0.11, -0.33, 0.55, ..., 0.77]  # Very similar!
"I hate broccoli"       → [-0.45, 0.23, -0.12, ..., 0.34] # Very different
```

### Visualization

```
                    "Python programming"
                           ●
                          /
                         /
"I love Python" ●───────●
                         \
                          \
                           ● "Python is great"


        "I hate vegetables" ●



                              (2D projection of 1536D space)
```

---

## 2. How Embeddings Work

### The Embedding Model

```
┌─────────────────────────────────────────────────────────┐
│                    Embedding Model                       │
│                                                          │
│  "The quick brown fox"  →  [Neural Network]  →  [0.1, 0.3, ...] │
│                                                          │
│  Trained on billions of text examples                    │
│  Learned relationships between words and concepts        │
└─────────────────────────────────────────────────────────┘
```

### Key Properties

| Property      | Meaning                                           |
| ------------- | ------------------------------------------------- |
| **Dimension** | Number of values in vector (e.g., 1536, 768, 384) |
| **Magnitude** | Length of vector (often normalized to 1)          |
| **Direction** | Encodes meaning                                   |

### Semantic Properties

```python
# Embeddings capture relationships
king - man + woman ≈ queen

# Similar concepts cluster together
# ["cat", "dog", "hamster"] are close
# ["car", "truck", "bus"] are close
# But animals and vehicles are far apart
```

---

## 3. OpenAI Embeddings

### Installation

```bash
uv add openai
```

### Basic Usage

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello, world!"
)

embedding = response.data[0].embedding
print(f"Dimension: {len(embedding)}")  # 1536
print(f"First 5 values: {embedding[:5]}")
```

### Batch Embeddings

```python
texts = [
    "Python programming",
    "JavaScript development",
    "Machine learning basics"
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)

embeddings = [item.embedding for item in response.data]
print(f"Got {len(embeddings)} embeddings")
```

### Available Models

| Model                  | Dimensions | Use Case                        | Cost |
| ---------------------- | ---------- | ------------------------------- | ---- |
| text-embedding-3-small | 1536       | General purpose, cost-effective | $    |
| text-embedding-3-large | 3072       | Highest quality                 | $$   |
| text-embedding-ada-002 | 1536       | Legacy (deprecated)             | $    |

### Dimension Reduction

Reduce dimensions to save storage (with some quality loss):

```python
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Hello, world!",
    dimensions=512  # Reduce from 1536 to 512
)
```

---

## 4. Open-Source Embeddings

### Sentence Transformers

```bash
uv add sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer

# Load a model (downloads on first use)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Single text
embedding = model.encode("Hello, world!")
print(f"Dimension: {len(embedding)}")  # 384

# Batch
texts = ["First text", "Second text", "Third text"]
embeddings = model.encode(texts)
print(f"Shape: {embeddings.shape}")  # (3, 384)
```

### Popular Models

| Model             | Dimensions | Speed   | Quality |
| ----------------- | ---------- | ------- | ------- |
| all-MiniLM-L6-v2  | 384        | ⚡ Fast | Good    |
| all-mpnet-base-v2 | 768        | Medium  | Better  |
| bge-large-en-v1.5 | 1024       | Slower  | Best    |
| gte-large         | 1024       | Slower  | Best    |

### GPU Acceleration

```python
model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
# or for Apple Silicon
model = SentenceTransformer("all-MiniLM-L6-v2", device="mps")
```

---

## 5. Similarity Metrics

### Cosine Similarity

Most common metric. Measures angle between vectors (ignores magnitude):

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Range: -1 to 1
# 1 = identical direction (same meaning)
# 0 = perpendicular (unrelated)
# -1 = opposite (rare in practice)
```

### Dot Product

Fast when vectors are normalized:

```python
def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b)

# If vectors are normalized (magnitude = 1):
# dot_product == cosine_similarity
```

### Euclidean Distance

Measures straight-line distance:

```python
def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return np.linalg.norm(a - b)

# Lower = more similar
# Range: 0 to infinity
```

### Which to Use?

| Metric          | Best For           | Note                |
| --------------- | ------------------ | ------------------- |
| **Cosine**      | Most text tasks    | Ignore magnitude    |
| **Dot Product** | Normalized vectors | Fastest             |
| **Euclidean**   | Geometric tasks    | Considers magnitude |

---

## 6. Practical Patterns

### Embedding Cache

Avoid re-computing embeddings:

```python
import hashlib
import json
from pathlib import Path

class EmbeddingCache:
    def __init__(self, cache_dir: str = ".embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _hash(self, text: str, model: str) -> str:
        content = f"{model}:{text}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, text: str, model: str) -> list[float] | None:
        path = self.cache_dir / f"{self._hash(text, model)}.json"
        if path.exists():
            return json.loads(path.read_text())
        return None

    def set(self, text: str, model: str, embedding: list[float]):
        path = self.cache_dir / f"{self._hash(text, model)}.json"
        path.write_text(json.dumps(embedding))

# Usage
cache = EmbeddingCache()
embedding = cache.get(text, "text-embedding-3-small")
if not embedding:
    embedding = get_embedding(text)
    cache.set(text, "text-embedding-3-small", embedding)
```

### Batch Processing

```python
from openai import OpenAI
from typing import Iterator

def batch_embed(
    texts: list[str],
    batch_size: int = 100,
    model: str = "text-embedding-3-small"
) -> list[list[float]]:
    """Embed texts in batches to avoid API limits."""
    client = OpenAI()
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model=model,
            input=batch
        )
        all_embeddings.extend([item.embedding for item in response.data])

    return all_embeddings
```

### Semantic Search

```python
import numpy as np
from dataclasses import dataclass

@dataclass
class SearchResult:
    text: str
    score: float
    index: int

def semantic_search(
    query: str,
    documents: list[str],
    doc_embeddings: np.ndarray,
    top_k: int = 5
) -> list[SearchResult]:
    """Find most similar documents to query."""
    # Embed query
    query_embedding = get_embedding(query)

    # Calculate similarities
    similarities = np.dot(doc_embeddings, query_embedding)

    # Get top-k
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    return [
        SearchResult(
            text=documents[i],
            score=float(similarities[i]),
            index=i
        )
        for i in top_indices
    ]

# Usage
docs = ["Python is great", "JavaScript is popular", "Rust is fast"]
embeddings = np.array([get_embedding(d) for d in docs])

results = semantic_search("programming languages", docs, embeddings)
for r in results:
    print(f"{r.score:.3f}: {r.text}")
```

---

## 7. Choosing the Right Model

### Decision Matrix

| Factor  | OpenAI           | Sentence Transformers |
| ------- | ---------------- | --------------------- |
| Quality | Excellent        | Good to Excellent     |
| Speed   | API latency      | Local (fast)          |
| Cost    | Pay per token    | Free                  |
| Privacy | Data sent to API | Local processing      |
| Offline | No               | Yes                   |

### Recommendations

```python
# Production, quality critical, budget exists
model = "text-embedding-3-large"

# Production, cost-sensitive
model = "text-embedding-3-small"

# Local/offline, privacy critical
model = SentenceTransformer("all-MiniLM-L6-v2")

# Best open-source quality
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
```

---

## 8. Common Pitfalls

### ❌ Different Models = Different Spaces

```python
# WRONG: Can't compare embeddings from different models
emb1 = openai_embed("hello")     # 1536 dims
emb2 = minilm_embed("hello")     # 384 dims
similarity(emb1, emb2)           # Meaningless!
```

### ❌ Forgetting to Normalize

```python
# Some models return normalized vectors, some don't
# Check before using dot product

# Normalize if needed
embedding = embedding / np.linalg.norm(embedding)
```

### ❌ Embedding Long Text

```python
# Models have max input length (typically 512-8192 tokens)
# Very long texts get truncated!

# Solution: Chunk first, then embed
chunks = chunk_text(long_document, max_tokens=512)
embeddings = [embed(chunk) for chunk in chunks]
```

---

## Quick Reference

### OpenAI

```python
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(model="text-embedding-3-small", input=text)
embedding = response.data[0].embedding
```

### Sentence Transformers

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embedding = model.encode(text)
```

### Cosine Similarity

```python
similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

---

## Summary

You've learned:

1. **What embeddings are** — meaning as vectors
2. **OpenAI embeddings** — API usage, models
3. **Sentence Transformers** — local, open-source
4. **Similarity metrics** — cosine, dot product, euclidean
5. **Practical patterns** — caching, batching, search
6. **Model selection** — when to use what

Next chapter: Vector Stores — storing and searching embeddings at scale.
