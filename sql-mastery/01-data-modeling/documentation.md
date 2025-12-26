# Chapter 1: Data Modeling — Designing for Scale

> _"Good schema design prevents 90% of query headaches."_

---

## What You'll Learn

- Entity-relationship modeling
- Normalization (1NF, 2NF, 3NF)
- Denormalization trade-offs
- Primary keys, foreign keys, indexes
- Schema patterns for AI applications

---

## 1. Entity-Relationship Basics

### Entities and Attributes

```sql
-- Entity: User
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Entity: Conversation (for AI chat)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Relationship Types

```
1:1  - User ↔ Profile
1:N  - User ↔ Conversations
N:N  - Users ↔ Tags (via junction table)
```

---

## 2. Normalization

### First Normal Form (1NF)

- No repeating groups
- Atomic values only

```sql
-- BAD: Repeating group
CREATE TABLE users (
    id INT,
    phone1 VARCHAR(20),
    phone2 VARCHAR(20)
);

-- GOOD: Separate table
CREATE TABLE user_phones (
    user_id INT REFERENCES users(id),
    phone VARCHAR(20)
);
```

### Second Normal Form (2NF)

- 1NF + no partial dependencies

### Third Normal Form (3NF)

- 2NF + no transitive dependencies

---

## 3. Keys and Indexes

### Primary Keys

```sql
-- Serial (auto-increment)
id SERIAL PRIMARY KEY

-- UUID (distributed-friendly)
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### Foreign Keys

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    FOREIGN KEY (conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);
```

### Indexes

```sql
-- Single column
CREATE INDEX idx_users_email ON users(email);

-- Composite
CREATE INDEX idx_messages_conv_time
    ON messages(conversation_id, created_at);

-- Partial (conditional)
CREATE INDEX idx_active_users
    ON users(email)
    WHERE is_active = true;
```

---

## 4. AI Application Schemas

### Chat History

```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id),
    model VARCHAR(50) DEFAULT 'gpt-4o',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON chat_messages(session_id, created_at);
```

### Document Store (RAG)

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    collection_id UUID,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT NOT NULL,
    embedding vector(1536),  -- pgvector
    metadata JSONB DEFAULT '{}'
);
```

---

## 5. Schema Evolution

### Migrations Best Practices

```sql
-- Add column (safe)
ALTER TABLE users ADD COLUMN api_key VARCHAR(64);

-- Add NOT NULL with default (safe)
ALTER TABLE users ADD COLUMN is_premium BOOLEAN NOT NULL DEFAULT false;

-- Rename column (careful)
ALTER TABLE users RENAME COLUMN name TO full_name;

-- Drop column (dangerous)
ALTER TABLE users DROP COLUMN legacy_field;
```

---

## Quick Reference

```sql
-- Create with relationships
CREATE TABLE child (
    id SERIAL PRIMARY KEY,
    parent_id INT REFERENCES parent(id) ON DELETE CASCADE
);

-- Composite index
CREATE INDEX idx_name ON table(col1, col2);

-- JSONB field
metadata JSONB DEFAULT '{}'
```

---

## Summary

1. **Entities** — Tables represent real-world objects
2. **Normalization** — Reduce redundancy
3. **Keys** — Primary, foreign, unique
4. **Indexes** — Speed up queries
5. **AI schemas** — Chat, documents, embeddings
