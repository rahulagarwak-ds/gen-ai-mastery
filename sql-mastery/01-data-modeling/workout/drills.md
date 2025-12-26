# Workout: Data Modeling

## Drill 1: Create Entity 🟢

```sql
-- Create a users table with:
-- id (serial primary key)
-- email (unique, not null)
-- created_at (timestamp, default now)
```

## Drill 2: Foreign Key 🟢

```sql
-- Create conversations table that references users
-- Add ON DELETE CASCADE
```

## Drill 3: Composite Index 🟡

```sql
-- Create index on (user_id, created_at) for messages table
```

## Drill 4: JSONB Column 🟡

```sql
-- Add metadata JSONB column with default '{}'
```

## Drill 5: Chat Schema 🟡

```sql
-- Design tables for: sessions, messages
-- Include role, content, tokens_used
```

## Drill 6: UUID Primary Key 🟡

```sql
-- Create table with UUID primary key using gen_random_uuid()
```

## Drill 7: Document Store 🔴

```sql
-- Design RAG schema: documents, chunks, embeddings
```

## Drill 8: Migration 🔴

```sql
-- Add column with NOT NULL and default value
```

---

## Self-Check

- [ ] Can design normalized schemas
- [ ] Can create appropriate indexes
- [ ] Can use JSONB effectively
- [ ] Can design AI application schemas
