# Chapter 2: Vector Stores — Searching at Scale

> _"You can't search millions of vectors with a for loop."_

---

## What You'll Learn

By the end of this chapter, you will understand:

- Why vector stores exist
- ChromaDB for local development
- Pinecone for production scale
- pgvector for PostgreSQL integration
- Index types and trade-offs
- Metadata filtering

---

## 1. Why Vector Stores?

### The Problem

Semantic search requires comparing a query against all documents:

```python
# Naive approach - O(n) for each query
for doc_embedding in all_embeddings:  # 1 million docs
    similarity(query_embedding, doc_embedding)
# Very slow!
```

### The Solution

Vector databases use approximate nearest neighbor (ANN) algorithms:

```
Traditional DB:  WHERE title LIKE '%python%'   (exact match)
Vector Store:    SIMILAR TO embedding(query)    (semantic match)
```

### Key Features

| Feature                    | Description                            |
| -------------------------- | -------------------------------------- |
| **Fast similarity search** | Find nearest neighbors in milliseconds |
| **Scalability**            | Handle millions/billions of vectors    |
| **Metadata filtering**     | Filter by tags, dates, categories      |
| **Persistence**            | Store embeddings durably               |

---

## 2. ChromaDB (Local Development)

### Installation

```bash
uv add chromadb
```

### Basic Usage

```python
import chromadb

# Create client (in-memory)
client = chromadb.Client()

# Create a collection
collection = client.create_collection("my_documents")

# Add documents
collection.add(
    documents=["Python is great", "JavaScript is popular", "Rust is fast"],
    ids=["doc1", "doc2", "doc3"],
    metadatas=[
        {"category": "programming", "year": 2024},
        {"category": "programming", "year": 2024},
        {"category": "programming", "year": 2023}
    ]
)

# Query
results = collection.query(
    query_texts=["What language is fast?"],
    n_results=2
)

print(results["documents"])
# [['Rust is fast', 'Python is great']]
```

### Persistent Storage

```python
# Persist to disk
client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection("my_docs")
```

### With Pre-computed Embeddings

```python
# If you have your own embeddings
collection.add(
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)

# Query with embedding
results = collection.query(
    query_embeddings=[[0.1, 0.2, ...]],
    n_results=5
)
```

### Metadata Filtering

```python
# Filter by metadata
results = collection.query(
    query_texts=["fast language"],
    n_results=5,
    where={"category": "programming"},
    where_document={"$contains": "fast"}
)

# Complex filters
results = collection.query(
    query_texts=["query"],
    where={
        "$and": [
            {"category": {"$eq": "programming"}},
            {"year": {"$gte": 2023}}
        ]
    }
)
```

### ChromaDB with OpenAI Embeddings

```python
import chromadb
from chromadb.utils import embedding_functions

# Use OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)

# Now add() will use OpenAI automatically
collection.add(
    documents=["Doc 1", "Doc 2"],
    ids=["id1", "id2"]
)
```

---

## 3. Pinecone (Production Scale)

### Installation

```bash
uv add pinecone-client
```

### Setup

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-api-key")

# Create index
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
)

# Connect to index
index = pc.Index("my-index")
```

### Upsert (Insert/Update)

```python
# Single upsert
index.upsert(
    vectors=[
        {
            "id": "doc1",
            "values": [0.1, 0.2, ...],  # 1536 dims
            "metadata": {"category": "tech", "year": 2024}
        }
    ]
)

# Batch upsert
vectors = [
    {"id": f"doc{i}", "values": embeddings[i], "metadata": metadata[i]}
    for i in range(len(documents))
]
index.upsert(vectors=vectors, batch_size=100)
```

### Query

```python
results = index.query(
    vector=[0.1, 0.2, ...],  # Query embedding
    top_k=5,
    include_metadata=True
)

for match in results.matches:
    print(f"ID: {match.id}, Score: {match.score}")
    print(f"Metadata: {match.metadata}")
```

### Metadata Filtering

```python
results = index.query(
    vector=query_embedding,
    top_k=5,
    filter={
        "category": {"$eq": "tech"},
        "year": {"$gte": 2023}
    }
)
```

### Namespaces

```python
# Separate data by namespace
index.upsert(vectors=user1_docs, namespace="user1")
index.upsert(vectors=user2_docs, namespace="user2")

# Query within namespace
results = index.query(
    vector=query,
    top_k=5,
    namespace="user1"
)
```

---

## 4. pgvector (PostgreSQL)

### When to Use

- Already using PostgreSQL
- Need ACID transactions
- Relational data + vectors
- Self-hosted solution

### Setup

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

### Python Usage

```python
import psycopg2
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect("postgresql://...")
register_vector(conn)

# Insert
cur = conn.cursor()
cur.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("Hello world", embedding)
)
conn.commit()

# Query
cur.execute("""
    SELECT content, embedding <=> %s AS distance
    FROM documents
    ORDER BY distance
    LIMIT 5
""", (query_embedding,))

for row in cur.fetchall():
    print(row)
```

### With SQLAlchemy

```python
from sqlalchemy import Column, Integer, Text
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    content = Column(Text)
    embedding = Column(Vector(1536))
```

---

## 5. Comparison

| Feature      | ChromaDB     | Pinecone    | pgvector       |
| ------------ | ------------ | ----------- | -------------- |
| **Setup**    | Simple       | Cloud       | PostgreSQL     |
| **Scale**    | Small-Medium | Large       | Medium-Large   |
| **Cost**     | Free         | Pay per use | Server cost    |
| **Speed**    | Fast         | Very Fast   | Fast           |
| **Hosting**  | Local/Self   | Managed     | Self           |
| **Best For** | Development  | Production  | Postgres users |

### Decision Tree

```
Need production scale? → Pinecone
Already using PostgreSQL? → pgvector
Development/prototyping? → ChromaDB
Self-hosted requirement? → pgvector or ChromaDB
```

---

## 6. Index Types

### HNSW (Hierarchical Navigable Small World)

- Used by ChromaDB, Pinecone
- Very fast queries
- Uses more memory

### IVF (Inverted File Index)

- Used by pgvector
- Balanced memory/speed
- Requires training

### Flat (Brute Force)

- Exact results
- O(n) per query
- Only for small datasets

```python
# pgvector index types
# IVF - good balance
CREATE INDEX ON docs USING ivfflat (embedding vector_cosine_ops);

# HNSW - faster queries, more memory
CREATE INDEX ON docs USING hnsw (embedding vector_cosine_ops);
```

---

## 7. Production Patterns

### Hybrid Search

Combine semantic + keyword search:

```python
from chromadb import Collection

def hybrid_search(
    collection: Collection,
    query: str,
    keywords: list[str],
    n_results: int = 5
) -> list[dict]:
    # Semantic search
    semantic_results = collection.query(
        query_texts=[query],
        n_results=n_results * 2
    )

    # Keyword filter
    filtered = []
    for doc, id_, score in zip(
        semantic_results["documents"][0],
        semantic_results["ids"][0],
        semantic_results["distances"][0]
    ):
        if any(kw.lower() in doc.lower() for kw in keywords):
            filtered.append({"id": id_, "doc": doc, "score": score})

    return filtered[:n_results]
```

### Multi-Tenant Isolation

```python
# Using collections per tenant
def get_tenant_collection(tenant_id: str):
    return client.get_or_create_collection(f"tenant_{tenant_id}")

# Using namespaces (Pinecone)
index.query(vector=query, namespace=f"tenant_{tenant_id}")

# Using metadata filter
collection.query(
    query_texts=[query],
    where={"tenant_id": tenant_id}
)
```

### Batch Operations

```python
def batch_upsert(
    collection: Collection,
    documents: list[str],
    ids: list[str],
    batch_size: int = 100
):
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        collection.add(documents=batch_docs, ids=batch_ids)
```

---

## Quick Reference

### ChromaDB

```python
client = chromadb.Client()
collection = client.create_collection("name")
collection.add(documents=[...], ids=[...])
results = collection.query(query_texts=["..."], n_results=5)
```

### Pinecone

```python
pc = Pinecone(api_key="...")
index = pc.Index("name")
index.upsert(vectors=[{"id": ..., "values": ...}])
results = index.query(vector=[...], top_k=5)
```

### pgvector

```sql
SELECT * FROM docs ORDER BY embedding <=> query LIMIT 5;
```

---

## Summary

You've learned:

1. **Why vector stores** — Scale similarity search
2. **ChromaDB** — Easy local development
3. **Pinecone** — Production-ready managed
4. **pgvector** — PostgreSQL integration
5. **Index types** — HNSW, IVF, flat
6. **Production patterns** — Hybrid search, multi-tenant

Next chapter: Document Processing — parsing, chunking, metadata.
