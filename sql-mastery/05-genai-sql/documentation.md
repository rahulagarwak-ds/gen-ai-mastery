# Chapter 5: Gen AI SQL — Vectors, Embeddings, RAG

> _"PostgreSQL + pgvector = production RAG without the complexity."_

---

## What You'll Learn

- pgvector extension
- Storing and querying embeddings
- Similarity search
- Hybrid search (vector + keyword)
- RAG data architecture

---

## 1. pgvector Setup

### Installation

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
```

### Vector Column

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding vector(1536),  -- OpenAI dimension
    metadata JSONB DEFAULT '{}'
);
```

---

## 2. Storing Embeddings

### Insert with Embedding

```sql
INSERT INTO documents (content, embedding, metadata)
VALUES (
    'Python is a programming language',
    '[0.1, 0.2, 0.3, ...]'::vector,  -- 1536 dimensions
    '{"source": "wiki", "page": 1}'
);
```

### Batch Insert (Python)

```python
from psycopg2.extras import execute_values

embeddings = get_embeddings(texts)  # From OpenAI

data = [(text, emb.tolist(), {}) for text, emb in zip(texts, embeddings)]

execute_values(
    cursor,
    "INSERT INTO documents (content, embedding, metadata) VALUES %s",
    data,
    template="(%s, %s::vector, %s::jsonb)"
)
```

---

## 3. Similarity Search

### Cosine Similarity

```sql
-- Most similar to query embedding
SELECT
    content,
    1 - (embedding <=> query_embedding) as similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

### Distance Operators

```sql
<=>  -- Cosine distance (most common for embeddings)
<->  -- L2 (Euclidean) distance
<#>  -- Inner product (negative, for max similarity)
```

### With Threshold

```sql
SELECT content, 1 - (embedding <=> $1) as similarity
FROM documents
WHERE 1 - (embedding <=> $1) > 0.8  -- Similarity threshold
ORDER BY embedding <=> $1
LIMIT 10;
```

---

## 4. Indexing for Performance

### HNSW Index (Recommended)

```sql
CREATE INDEX idx_docs_embedding_hnsw
ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### IVFFlat Index (Faster build)

```sql
-- First, cluster the data
CREATE INDEX idx_docs_embedding_ivf
ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### Query with Index

```sql
-- Set search params for accuracy/speed tradeoff
SET hnsw.ef_search = 100;

SELECT content FROM documents
ORDER BY embedding <=> $1
LIMIT 5;
```

---

## 5. Hybrid Search

### Full-Text + Vector

```sql
-- Add full-text search column
ALTER TABLE documents ADD COLUMN tsv tsvector;
UPDATE documents SET tsv = to_tsvector('english', content);
CREATE INDEX idx_docs_fts ON documents USING gin(tsv);
```

### Hybrid Query

```sql
WITH vector_results AS (
    SELECT id, content, 1 - (embedding <=> $1) as vector_score
    FROM documents
    ORDER BY embedding <=> $1
    LIMIT 20
),
keyword_results AS (
    SELECT id, content, ts_rank(tsv, plainto_tsquery($2)) as keyword_score
    FROM documents
    WHERE tsv @@ plainto_tsquery($2)
    LIMIT 20
)
SELECT
    COALESCE(v.id, k.id) as id,
    COALESCE(v.content, k.content) as content,
    COALESCE(v.vector_score, 0) * 0.7 +
    COALESCE(k.keyword_score, 0) * 0.3 as combined_score
FROM vector_results v
FULL OUTER JOIN keyword_results k ON v.id = k.id
ORDER BY combined_score DESC
LIMIT 10;
```

---

## 6. RAG Schema

### Complete RAG Tables

```sql
-- Collections (like ChromaDB collections)
CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents (original files)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID REFERENCES collections(id) ON DELETE CASCADE,
    source VARCHAR(500),
    title VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Chunks (embedded pieces)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT NOT NULL,
    embedding vector(1536),
    token_count INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_chunks_doc ON chunks(document_id);
CREATE INDEX idx_chunks_embedding
    ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_metadata ON chunks USING gin(metadata);
```

### RAG Query

```sql
-- Search with metadata filter
SELECT
    c.content,
    d.source,
    d.title,
    1 - (c.embedding <=> $1) as score
FROM chunks c
JOIN documents d ON c.document_id = d.id
WHERE d.collection_id = $2
AND c.metadata @> '{"type": "paragraph"}'  -- Filter
ORDER BY c.embedding <=> $1
LIMIT 5;
```

---

## 7. Chat History with Embeddings

```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER,
    title VARCHAR(255),
    summary_embedding vector(1536),  -- For semantic search
    created_at TIMESTAMP DEFAULT NOW()
);

-- Find similar past conversations
SELECT id, title
FROM chat_sessions
WHERE user_id = $1
ORDER BY summary_embedding <=> $2
LIMIT 5;
```

---

## Quick Reference

```sql
-- Cosine similarity search
ORDER BY embedding <=> query_vector LIMIT 5;

-- HNSW index
CREATE INDEX ON table USING hnsw (col vector_cosine_ops);

-- Similarity score
1 - (embedding <=> query_vector) as similarity

-- Metadata filter
WHERE metadata @> '{"key": "value"}'
```

---

## Summary

1. **pgvector** — Vector storage in PostgreSQL
2. **Similarity** — Cosine, L2, inner product
3. **Indexes** — HNSW for speed
4. **Hybrid search** — Vector + keyword
5. **RAG schema** — Collections, documents, chunks
