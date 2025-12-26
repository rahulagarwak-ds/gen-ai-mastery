# Chapter 4: RAG Pipeline — Bringing It All Together

> _"RAG is not just retrieval + generation. It's a system design problem."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Complete RAG pipeline architecture
- Ingestion vs retrieval pipelines
- Query transformation techniques
- Context augmentation strategies
- Reranking for better relevance
- Evaluation and debugging RAG

---

## 1. RAG Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       INGESTION PHASE                           │
│  Documents → Parse → Chunk → Embed → Store in Vector DB        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       RETRIEVAL PHASE                           │
│  Query → Embed → Search Vector DB → Retrieve Top-K Chunks      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       GENERATION PHASE                          │
│  Context + Query → LLM → Generated Answer                      │
└─────────────────────────────────────────────────────────────────┘
```

### Components

| Component       | Purpose                      |
| --------------- | ---------------------------- |
| Document Loader | Parse various file formats   |
| Chunker         | Split into embeddable pieces |
| Embedder        | Convert text to vectors      |
| Vector Store    | Store and search embeddings  |
| Retriever       | Find relevant chunks         |
| Reranker        | Improve retrieval quality    |
| Generator       | LLM that synthesizes answer  |

---

## 2. Ingestion Pipeline

```python
from dataclasses import dataclass
from typing import Iterator
import chromadb
from openai import OpenAI

@dataclass
class Document:
    content: str
    metadata: dict

class IngestionPipeline:
    def __init__(
        self,
        collection_name: str = "documents",
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        self.client = OpenAI()
        self.chroma = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.chroma.get_or_create_collection(collection_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed texts using OpenAI."""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]

    def chunk(self, text: str) -> list[str]:
        """Split text into chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks

    def ingest(self, documents: list[Document]) -> int:
        """Ingest documents into vector store."""
        all_chunks = []
        all_ids = []
        all_metadata = []

        for doc_idx, doc in enumerate(documents):
            chunks = self.chunk(doc.content)
            for chunk_idx, chunk in enumerate(chunks):
                chunk_id = f"doc{doc_idx}_chunk{chunk_idx}"
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append({
                    **doc.metadata,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks)
                })

        # Embed in batches
        embeddings = self.embed(all_chunks)

        # Store
        self.collection.add(
            embeddings=embeddings,
            documents=all_chunks,
            ids=all_ids,
            metadatas=all_metadata
        )

        return len(all_chunks)
```

---

## 3. Retrieval Pipeline

### Basic Retrieval

```python
class Retriever:
    def __init__(self, collection, embed_fn):
        self.collection = collection
        self.embed_fn = embed_fn

    def retrieve(
        self,
        query: str,
        k: int = 5,
        filter: dict = None
    ) -> list[dict]:
        """Retrieve relevant chunks."""
        query_embedding = self.embed_fn(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter
        )

        return [
            {
                "content": doc,
                "metadata": meta,
                "score": 1 - dist  # Convert distance to similarity
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
```

### Query Transformation

Improve retrieval by transforming queries:

```python
class QueryTransformer:
    def __init__(self, llm_client):
        self.llm = llm_client

    def expand_query(self, query: str) -> list[str]:
        """Generate multiple search queries from one."""
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Generate 3 alternative search queries for the given question. Return only the queries, one per line."
                },
                {"role": "user", "content": query}
            ]
        )

        queries = response.choices[0].message.content.strip().split("\n")
        return [query] + queries  # Include original

    def hypothetical_answer(self, query: str) -> str:
        """Generate a hypothetical answer to embed (HyDE)."""
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Write a short, hypothetical answer to this question as if you knew the answer."
                },
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
```

### Multi-Query Retrieval

```python
def multi_query_retrieve(
    retriever: Retriever,
    transformer: QueryTransformer,
    query: str,
    k: int = 5
) -> list[dict]:
    """Retrieve using multiple query variants."""
    queries = transformer.expand_query(query)

    all_results = {}
    for q in queries:
        results = retriever.retrieve(q, k=k)
        for r in results:
            # Deduplicate by content, keep highest score
            key = r["content"][:100]  # Use prefix as key
            if key not in all_results or r["score"] > all_results[key]["score"]:
                all_results[key] = r

    # Sort by score and return top-k
    sorted_results = sorted(all_results.values(), key=lambda x: -x["score"])
    return sorted_results[:k]
```

---

## 4. Reranking

### Cross-Encoder Reranking

More accurate than embedding similarity:

```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5
    ) -> list[dict]:
        """Rerank documents using cross-encoder."""
        pairs = [(query, doc["content"]) for doc in documents]
        scores = self.model.predict(pairs)

        # Add scores and sort
        for doc, score in zip(documents, scores):
            doc["rerank_score"] = float(score)

        sorted_docs = sorted(documents, key=lambda x: -x["rerank_score"])
        return sorted_docs[:top_k]
```

### LLM-Based Reranking

```python
def llm_rerank(
    query: str,
    documents: list[dict],
    llm_client,
    top_k: int = 5
) -> list[dict]:
    """Use LLM to rank relevance."""
    doc_text = "\n\n".join([
        f"[{i}] {doc['content'][:500]}"
        for i, doc in enumerate(documents)
    ])

    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Rank these documents by relevance to the query. Return only the indices in order of relevance, comma-separated."
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nDocuments:\n{doc_text}"
            }
        ]
    )

    indices = [int(i.strip()) for i in response.choices[0].message.content.split(",")]
    return [documents[i] for i in indices[:top_k]]
```

---

## 5. Generation

### Basic RAG Generation

```python
def generate_answer(
    query: str,
    context: list[dict],
    llm_client
) -> str:
    """Generate answer using retrieved context."""
    context_text = "\n\n".join([
        f"Source {i+1}:\n{doc['content']}"
        for i, doc in enumerate(context)
    ])

    response = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """Answer the question based on the provided context.

Rules:
- Only use information from the context
- If the context doesn't contain the answer, say "I don't have enough information"
- Cite sources using [Source N] format"""
            },
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {query}"
            }
        ]
    )

    return response.choices[0].message.content
```

### With Streaming

```python
def stream_answer(
    query: str,
    context: list[dict],
    llm_client
):
    """Stream the generated answer."""
    context_text = "\n\n".join([doc['content'] for doc in context])

    stream = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Answer based on context..."},
            {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {query}"}
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

---

## 6. Complete RAG Pipeline

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RAGResponse:
    answer: str
    sources: list[dict]
    query: str

class RAGPipeline:
    def __init__(
        self,
        collection_name: str = "documents",
        top_k: int = 5,
        use_reranker: bool = True
    ):
        self.openai = OpenAI()
        self.chroma = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.chroma.get_or_create_collection(collection_name)
        self.top_k = top_k
        self.use_reranker = use_reranker

        if use_reranker:
            self.reranker = Reranker()

    def embed(self, text: str) -> list[float]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def retrieve(self, query: str) -> list[dict]:
        """Retrieve relevant documents."""
        results = self.collection.query(
            query_embeddings=[self.embed(query)],
            n_results=self.top_k * 2 if self.use_reranker else self.top_k
        )

        docs = [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(
                results["documents"][0],
                results["metadatas"][0]
            )
        ]

        if self.use_reranker:
            docs = self.reranker.rerank(query, docs, self.top_k)

        return docs

    def generate(self, query: str, context: list[dict]) -> str:
        """Generate answer from context."""
        return generate_answer(query, context, self.openai)

    def query(self, question: str) -> RAGResponse:
        """End-to-end RAG query."""
        # Retrieve
        sources = self.retrieve(question)

        # Generate
        answer = self.generate(question, sources)

        return RAGResponse(
            answer=answer,
            sources=sources,
            query=question
        )

# Usage
rag = RAGPipeline()
response = rag.query("What is the capital of France?")
print(response.answer)
print(f"Based on {len(response.sources)} sources")
```

---

## 7. Advanced Patterns

### Hybrid Search

Combine semantic + keyword:

```python
def hybrid_search(
    query: str,
    collection,
    embed_fn,
    k: int = 5,
    semantic_weight: float = 0.7
) -> list[dict]:
    """Combine semantic and keyword search."""
    # Semantic search
    semantic_results = collection.query(
        query_embeddings=[embed_fn(query)],
        n_results=k * 2
    )

    # Keyword search (using where_document)
    keywords = query.lower().split()
    keyword_results = collection.query(
        query_texts=[query],
        n_results=k * 2,
        where_document={"$contains": keywords[0]} if keywords else None
    )

    # Combine and score
    combined = {}
    for doc, dist in zip(semantic_results["documents"][0], semantic_results["distances"][0]):
        combined[doc] = semantic_weight * (1 - dist)

    for doc, dist in zip(keyword_results["documents"][0], keyword_results["distances"][0]):
        keyword_score = (1 - semantic_weight) * (1 - dist)
        combined[doc] = combined.get(doc, 0) + keyword_score

    sorted_docs = sorted(combined.items(), key=lambda x: -x[1])
    return [{"content": doc, "score": score} for doc, score in sorted_docs[:k]]
```

### Self-Query

Let LLM write the filter:

```python
def self_query(
    query: str,
    llm_client
) -> tuple[str, dict]:
    """Extract search query and metadata filter."""
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Extract a search query and metadata filter from the user's question.

Available metadata fields: category, year, author
Return JSON: {"query": "...", "filter": {...}}"""
            },
            {"role": "user", "content": query}
        ],
        response_format={"type": "json_object"}
    )

    import json
    result = json.loads(response.choices[0].message.content)
    return result["query"], result.get("filter", {})
```

---

## 8. Evaluation

### Retrieval Metrics

```python
def evaluate_retrieval(
    queries: list[str],
    expected_docs: list[list[str]],
    retriever: Retriever,
    k: int = 5
) -> dict:
    """Evaluate retrieval quality."""
    hits_at_k = 0
    mrr_sum = 0

    for query, expected in zip(queries, expected_docs):
        results = retriever.retrieve(query, k=k)
        retrieved_docs = [r["content"] for r in results]

        # Hit@K
        if any(exp in retrieved_docs for exp in expected):
            hits_at_k += 1

        # MRR
        for i, doc in enumerate(retrieved_docs):
            if doc in expected:
                mrr_sum += 1 / (i + 1)
                break

    return {
        "hit_rate": hits_at_k / len(queries),
        "mrr": mrr_sum / len(queries)
    }
```

---

## Quick Reference

### Pipeline

```python
rag = RAGPipeline()
response = rag.query("question")
print(response.answer, response.sources)
```

### Ingestion

```python
pipeline.ingest([Document(content="...", metadata={})])
```

### Retrieval + Reranking

```python
docs = retriever.retrieve(query, k=10)
reranked = reranker.rerank(query, docs, top_k=5)
```

---

## Summary

You've learned:

1. **RAG architecture** — Ingestion, retrieval, generation
2. **Ingestion pipeline** — Load, chunk, embed, store
3. **Query transformation** — Expansion, HyDE
4. **Reranking** — Cross-encoder, LLM-based
5. **Generation** — Grounded answer synthesis
6. **Advanced patterns** — Hybrid search, self-query
7. **Evaluation** — Hit rate, MRR

**Month 3 Complete!** You can now build production RAG systems.
