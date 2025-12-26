# Chapter 5: Advanced RAG — Production-Grade Retrieval

> _"The difference between a demo and production is in the details."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Query rewriting and expansion
- Hybrid search (dense + sparse)
- Reranking with cross-encoders
- Semantic caching for low latency
- Streaming and async patterns

---

## 1. Query Rewriting

### Why Rewrite Queries?

User queries are often:

- Ambiguous ("How do I fix it?")
- Incomplete ("Python error")
- Conversational ("And what about the other one?")

### Query Expansion with LLM

```python
from openai import OpenAI

client = OpenAI()

def expand_query(query: str, n: int = 3) -> list[str]:
    """Generate multiple search queries from user query."""

    prompt = f"""Generate {n} different search queries to find information for:
"{query}"

Return only the queries, one per line."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    queries = response.choices[0].message.content.strip().split("\n")
    return [query] + queries[:n]  # Include original

# Example
queries = expand_query("How to optimize RAG latency?")
# ["How to optimize RAG latency?",
#  "RAG system performance optimization techniques",
#  "Reduce retrieval latency in vector search",
#  "Speed up LLM response with caching"]
```

### HyDE (Hypothetical Document Embeddings)

```python
def hyde_query(query: str) -> str:
    """Generate hypothetical answer to embed instead of query."""

    prompt = f"""Write a short passage that would answer this question:
"{query}"

Write as if you found this in a document."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# Query: "What is HNSW?"
# HyDE: "HNSW (Hierarchical Navigable Small World) is an algorithm
#        for approximate nearest neighbor search. It builds a multi-layer
#        graph structure that enables efficient similarity search..."
```

---

## 2. Hybrid Search

### Combining Dense and Sparse Retrieval

```python
from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    def __init__(self, documents: list[str], embeddings: np.ndarray):
        self.documents = documents
        self.embeddings = embeddings

        # Sparse: BM25
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(
        self,
        query: str,
        query_embedding: np.ndarray,
        k: int = 5,
        alpha: float = 0.5  # Weight for dense vs sparse
    ) -> list[tuple[int, float]]:
        """
        alpha=1.0 → Pure dense (semantic)
        alpha=0.0 → Pure sparse (keyword)
        alpha=0.5 → Balanced hybrid
        """

        # Dense scores (cosine similarity)
        dense_scores = np.dot(self.embeddings, query_embedding)
        dense_scores = (dense_scores + 1) / 2  # Normalize to 0-1

        # Sparse scores (BM25)
        sparse_scores = self.bm25.get_scores(query.lower().split())
        sparse_scores = sparse_scores / (sparse_scores.max() + 1e-8)  # Normalize

        # Combine
        combined = alpha * dense_scores + (1 - alpha) * sparse_scores

        # Top-k
        top_indices = np.argsort(combined)[::-1][:k]
        return [(i, combined[i]) for i in top_indices]
```

### Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(
    rankings: list[list[int]],  # Multiple ranked lists
    k: int = 60
) -> list[tuple[int, float]]:
    """Combine multiple rankings using RRF."""

    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank + 1)

    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_docs
```

---

## 3. Reranking

### Cross-Encoder Reranking

```python
from sentence_transformers import CrossEncoder

# Load reranker model
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(
    query: str,
    documents: list[str],
    top_k: int = 5
) -> list[tuple[str, float]]:
    """Rerank documents using cross-encoder."""

    # Create pairs
    pairs = [[query, doc] for doc in documents]

    # Score all pairs
    scores = reranker.predict(pairs)

    # Sort by score
    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)

    return ranked[:top_k]

# Usage
initial_results = vector_store.search(query, k=20)  # Retrieve many
reranked = rerank(query, initial_results, top_k=5)  # Rerank to top 5
```

### Cohere Rerank API

```python
import cohere

co = cohere.Client()

def cohere_rerank(
    query: str,
    documents: list[str],
    top_n: int = 5
) -> list[dict]:
    """Use Cohere's rerank API."""

    response = co.rerank(
        model="rerank-english-v3.0",
        query=query,
        documents=documents,
        top_n=top_n
    )

    return [
        {"text": documents[r.index], "score": r.relevance_score}
        for r in response.results
    ]
```

---

## 4. Semantic Caching

### Query-Level Cache

```python
import hashlib
import json
from pathlib import Path
import numpy as np

class SemanticCache:
    def __init__(
        self,
        cache_dir: str = ".cache",
        similarity_threshold: float = 0.95,
        embed_fn=None
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.threshold = similarity_threshold
        self.embed_fn = embed_fn

        self._cache = {}  # query_hash -> {embedding, response}
        self._load_cache()

    def _hash(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:12]

    def _load_cache(self):
        cache_file = self.cache_dir / "semantic_cache.json"
        if cache_file.exists():
            self._cache = json.loads(cache_file.read_text())

    def _save_cache(self):
        cache_file = self.cache_dir / "semantic_cache.json"
        cache_file.write_text(json.dumps(self._cache))

    def get(self, query: str) -> str | None:
        """Check cache for semantically similar query."""
        query_embedding = self.embed_fn(query)

        for cached in self._cache.values():
            cached_embedding = np.array(cached["embedding"])
            similarity = np.dot(query_embedding, cached_embedding)

            if similarity >= self.threshold:
                return cached["response"]

        return None

    def set(self, query: str, response: str):
        """Cache a query-response pair."""
        query_hash = self._hash(query)
        self._cache[query_hash] = {
            "query": query,
            "embedding": self.embed_fn(query).tolist(),
            "response": response
        }
        self._save_cache()
```

### Embedding Cache

```python
import hashlib
import pickle
from pathlib import Path

class EmbeddingCache:
    def __init__(self, cache_dir: str = ".embedding_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> list[float] | None:
        cache_file = self.cache_dir / f"{self._hash(text)}.pkl"
        if cache_file.exists():
            return pickle.loads(cache_file.read_bytes())
        return None

    def set(self, text: str, embedding: list[float]):
        cache_file = self.cache_dir / f"{self._hash(text)}.pkl"
        cache_file.write_bytes(pickle.dumps(embedding))

    def get_or_compute(self, text: str, embed_fn) -> list[float]:
        cached = self.get(text)
        if cached:
            return cached
        embedding = embed_fn(text)
        self.set(text, embedding)
        return embedding
```

---

## 5. Latency Optimization

### Streaming Responses

```python
from openai import OpenAI

client = OpenAI()

def stream_rag_response(query: str, context: list[str]):
    """Stream the RAG response token by token."""

    context_str = "\n\n".join(context)

    prompt = f"""Answer based on this context:

{context_str}

Question: {query}"""

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Usage
for token in stream_rag_response("What is Python?", ["Python is..."]):
    print(token, end="", flush=True)
```

### Async Retrieval

```python
import asyncio
import httpx

async def async_retrieve(queries: list[str], embed_fn, vector_store):
    """Retrieve for multiple queries concurrently."""

    async def retrieve_one(query: str):
        embedding = embed_fn(query)
        return vector_store.search(embedding, k=5)

    tasks = [retrieve_one(q) for q in queries]
    results = await asyncio.gather(*tasks)

    # Deduplicate and merge
    seen = set()
    merged = []
    for result_list in results:
        for doc in result_list:
            if doc.id not in seen:
                seen.add(doc.id)
                merged.append(doc)

    return merged
```

### Pre-computation Strategies

```python
class OptimizedRAG:
    def __init__(self, documents: list[str]):
        self.documents = documents

        # Pre-compute embeddings at init
        self.embeddings = self._batch_embed(documents)

        # Pre-build BM25 index
        self.bm25 = self._build_bm25(documents)

    def _batch_embed(self, texts: list[str], batch_size: int = 100):
        """Batch embedding for efficiency."""
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = embed_fn(batch)  # Batch API call
            embeddings.extend(batch_embeddings)
        return embeddings
```

---

## 6. Production RAG Pipeline

```python
from dataclasses import dataclass
from typing import Generator

@dataclass
class RAGConfig:
    use_hybrid: bool = True
    use_rerank: bool = True
    use_cache: bool = True
    rerank_top_k: int = 5
    retrieve_top_k: int = 20
    cache_threshold: float = 0.95

class ProductionRAG:
    def __init__(self, config: RAGConfig = RAGConfig()):
        self.config = config
        self.cache = SemanticCache() if config.use_cache else None
        self.retriever = HybridRetriever() if config.use_hybrid else DenseRetriever()
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def query(self, question: str) -> Generator[str, None, None]:
        """Full production RAG with streaming."""

        # 1. Check cache
        if self.cache:
            cached = self.cache.get(question)
            if cached:
                yield cached
                return

        # 2. Query expansion
        queries = expand_query(question, n=2)

        # 3. Retrieve
        results = self.retriever.search(queries, k=self.config.retrieve_top_k)

        # 4. Rerank
        if self.config.use_rerank:
            results = rerank(question, results, top_k=self.config.rerank_top_k)

        # 5. Generate with streaming
        response_parts = []
        for token in stream_rag_response(question, results):
            response_parts.append(token)
            yield token

        # 6. Cache response
        if self.cache:
            self.cache.set(question, "".join(response_parts))
```

---

## Quick Reference

### Query Expansion

```python
queries = expand_query(query, n=3)
```

### Hybrid Search

```python
retriever = HybridRetriever(docs, embeddings)
results = retriever.search(query, query_emb, alpha=0.5)
```

### Reranking

```python
reranked = rerank(query, documents, top_k=5)
```

### Semantic Cache

```python
cache = SemanticCache(threshold=0.95, embed_fn=embed)
cached = cache.get(query) or generate_and_cache(query)
```

---

## Summary

You've learned:

1. **Query rewriting** — Expansion, HyDE
2. **Hybrid search** — Dense + sparse, RRF
3. **Reranking** — Cross-encoders, Cohere
4. **Caching** — Semantic and embedding caches
5. **Latency** — Streaming, async, batching

This completes your RAG toolkit for production systems.
