# Chapter 2: Advanced SQL — Beyond the Basics

> _"CTEs and window functions separate juniors from seniors."_

---

## What You'll Learn

- Common Table Expressions (CTEs)
- Window functions
- Recursive queries
- JSON/JSONB operations
- Advanced joins

---

## 1. Common Table Expressions (CTEs)

### Basic CTE

```sql
WITH active_users AS (
    SELECT id, email, created_at
    FROM users
    WHERE is_active = true
)
SELECT * FROM active_users WHERE created_at > '2024-01-01';
```

### Multiple CTEs

```sql
WITH
user_stats AS (
    SELECT user_id, COUNT(*) as msg_count
    FROM messages
    GROUP BY user_id
),
active_users AS (
    SELECT id, email FROM users WHERE is_active = true
)
SELECT
    u.email,
    COALESCE(s.msg_count, 0) as total_messages
FROM active_users u
LEFT JOIN user_stats s ON u.id = s.user_id;
```

### Recursive CTE

```sql
-- Org hierarchy
WITH RECURSIVE org_tree AS (
    -- Base case
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case
    SELECT e.id, e.name, e.manager_id, t.level + 1
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree ORDER BY level;
```

---

## 2. Window Functions

### ROW_NUMBER, RANK, DENSE_RANK

```sql
SELECT
    user_id,
    score,
    ROW_NUMBER() OVER (ORDER BY score DESC) as row_num,
    RANK() OVER (ORDER BY score DESC) as rank,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank
FROM user_scores;
```

### Partitioned Windows

```sql
-- Rank within each category
SELECT
    category,
    product,
    sales,
    RANK() OVER (PARTITION BY category ORDER BY sales DESC) as category_rank
FROM products;
```

### LAG and LEAD

```sql
-- Compare with previous row
SELECT
    date,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY date) as prev_day,
    revenue - LAG(revenue, 1) OVER (ORDER BY date) as daily_change
FROM daily_revenue;
```

### Running Totals

```sql
SELECT
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total,
    AVG(amount) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7d_avg
FROM transactions;
```

---

## 3. JSON/JSONB Operations

### Extracting Data

```sql
-- -> returns JSON, ->> returns text
SELECT
    metadata->>'source' as source,
    metadata->>'page' as page,
    (metadata->'tokens')::int as tokens
FROM documents;
```

### Querying JSONB

```sql
-- Contains operator
SELECT * FROM documents WHERE metadata @> '{"type": "pdf"}';

-- Key exists
SELECT * FROM documents WHERE metadata ? 'author';

-- Path query
SELECT * FROM documents WHERE metadata #>> '{nested,key}' = 'value';
```

### Modifying JSONB

```sql
-- Add/update key
UPDATE documents
SET metadata = metadata || '{"processed": true}'
WHERE id = 1;

-- Remove key
UPDATE documents
SET metadata = metadata - 'temp_field';
```

### JSONB Aggregation

```sql
SELECT
    user_id,
    jsonb_agg(jsonb_build_object('role', role, 'content', content)) as messages
FROM chat_messages
GROUP BY user_id;
```

---

## 4. Advanced Joins

### Self Join

```sql
-- Find users who referred each other
SELECT
    u1.name as user,
    u2.name as referred_by
FROM users u1
JOIN users u2 ON u1.referred_by = u2.id;
```

### Lateral Join

```sql
-- Get top 3 messages per user
SELECT u.name, m.*
FROM users u
CROSS JOIN LATERAL (
    SELECT * FROM messages
    WHERE user_id = u.id
    ORDER BY created_at DESC
    LIMIT 3
) m;
```

### Anti-Join (NOT EXISTS)

```sql
-- Users with no messages
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM messages m WHERE m.user_id = u.id
);
```

---

## 5. Useful Patterns

### UPSERT (INSERT ON CONFLICT)

```sql
INSERT INTO settings (user_id, key, value)
VALUES (1, 'theme', 'dark')
ON CONFLICT (user_id, key)
DO UPDATE SET value = EXCLUDED.value;
```

### Conditional Aggregation

```sql
SELECT
    user_id,
    COUNT(*) FILTER (WHERE role = 'user') as user_messages,
    COUNT(*) FILTER (WHERE role = 'assistant') as ai_messages
FROM messages
GROUP BY user_id;
```

---

## Quick Reference

```sql
-- CTE
WITH name AS (SELECT ...) SELECT * FROM name;

-- Window
RANK() OVER (PARTITION BY x ORDER BY y)

-- JSONB
metadata->>'key'  -- text
metadata @> '{}'  -- contains

-- Running total
SUM(x) OVER (ORDER BY date)
```

---

## Summary

1. **CTEs** — Readable subqueries, recursion
2. **Window functions** — Ranking, running totals
3. **JSONB** — Flexible schema storage
4. **Lateral joins** — Correlated subqueries
5. **Patterns** — Upsert, conditional aggregation
