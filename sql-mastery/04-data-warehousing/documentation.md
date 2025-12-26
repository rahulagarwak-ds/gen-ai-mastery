# Chapter 4: Data Warehousing — Designing for Scale

> _"OLTP is for transactions. OLAP is for insights."_

---

## What You'll Learn

- OLTP vs OLAP
- Star schema and snowflake schema
- Fact and dimension tables
- Slowly Changing Dimensions (SCD)
- Partitioning and performance

---

## 1. OLTP vs OLAP

| Aspect        | OLTP             | OLAP            |
| ------------- | ---------------- | --------------- |
| Purpose       | Transactions     | Analytics       |
| Queries       | Simple, frequent | Complex, fewer  |
| Normalization | 3NF              | Denormalized    |
| Data          | Current          | Historical      |
| Example       | User signups     | Monthly reports |

---

## 2. Star Schema

### Structure

```
            ┌─────────────┐
            │  dim_user   │
            └──────┬──────┘
                   │
┌─────────────┐    │    ┌─────────────┐
│  dim_model  │────┼────│  dim_time   │
└─────────────┘    │    └─────────────┘
                   │
            ┌──────┴──────┐
            │ fact_llm_   │
            │  requests   │
            └─────────────┘
```

### Dimension Tables

```sql
-- Time dimension
CREATE TABLE dim_time (
    time_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    day_of_week INTEGER,
    week_of_year INTEGER,
    month INTEGER,
    quarter INTEGER,
    year INTEGER,
    is_weekend BOOLEAN
);

-- User dimension
CREATE TABLE dim_user (
    user_key SERIAL PRIMARY KEY,
    user_id INTEGER,  -- Natural key
    email VARCHAR(255),
    plan VARCHAR(50),
    signup_date DATE,
    -- SCD Type 2 fields
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    is_current BOOLEAN
);

-- Model dimension
CREATE TABLE dim_model (
    model_key SERIAL PRIMARY KEY,
    model_id VARCHAR(50),
    provider VARCHAR(50),
    family VARCHAR(50),
    input_cost_per_1k DECIMAL(10,6),
    output_cost_per_1k DECIMAL(10,6)
);
```

### Fact Table

```sql
CREATE TABLE fact_llm_requests (
    request_id UUID PRIMARY KEY,
    -- Dimension keys
    time_key INTEGER REFERENCES dim_time(time_id),
    user_key INTEGER REFERENCES dim_user(user_key),
    model_key INTEGER REFERENCES dim_model(model_key),
    -- Measures
    input_tokens INTEGER,
    output_tokens INTEGER,
    latency_ms INTEGER,
    cost_usd DECIMAL(10,6),
    -- Metadata
    created_at TIMESTAMP
);
```

---

## 3. Slowly Changing Dimensions

### SCD Type 1: Overwrite

```sql
-- Just update the row
UPDATE dim_user SET plan = 'premium' WHERE user_id = 123;
```

### SCD Type 2: Add New Row

```sql
-- Close old record
UPDATE dim_user
SET valid_to = NOW(), is_current = false
WHERE user_id = 123 AND is_current = true;

-- Insert new record
INSERT INTO dim_user (user_id, email, plan, valid_from, valid_to, is_current)
VALUES (123, 'user@example.com', 'premium', NOW(), '9999-12-31', true);
```

### Querying SCD Type 2

```sql
-- Current state
SELECT * FROM dim_user WHERE is_current = true;

-- Historical state at a point in time
SELECT * FROM dim_user
WHERE user_id = 123
AND '2024-01-15' BETWEEN valid_from AND valid_to;
```

---

## 4. Partitioning

### Range Partitioning (by date)

```sql
CREATE TABLE fact_requests (
    id UUID,
    created_at TIMESTAMP,
    user_id INTEGER,
    tokens INTEGER
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE fact_requests_2024_01
    PARTITION OF fact_requests
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE fact_requests_2024_02
    PARTITION OF fact_requests
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

### List Partitioning

```sql
CREATE TABLE events (
    id UUID,
    event_type VARCHAR(50),
    data JSONB
) PARTITION BY LIST (event_type);

CREATE TABLE events_chat PARTITION OF events
    FOR VALUES IN ('chat_start', 'chat_message', 'chat_end');

CREATE TABLE events_auth PARTITION OF events
    FOR VALUES IN ('login', 'logout', 'signup');
```

---

## 5. Aggregation Tables

### Pre-computed Summaries

```sql
-- Daily aggregates
CREATE TABLE agg_daily_usage (
    date DATE,
    user_id INTEGER,
    total_requests INTEGER,
    total_tokens INTEGER,
    total_cost DECIMAL(10,4),
    avg_latency DECIMAL(10,2),
    PRIMARY KEY (date, user_id)
);

-- Refresh daily
INSERT INTO agg_daily_usage
SELECT
    DATE(created_at),
    user_id,
    COUNT(*),
    SUM(tokens),
    SUM(cost),
    AVG(latency_ms)
FROM fact_llm_requests
WHERE DATE(created_at) = CURRENT_DATE - 1
GROUP BY DATE(created_at), user_id
ON CONFLICT (date, user_id) DO UPDATE SET
    total_requests = EXCLUDED.total_requests,
    total_tokens = EXCLUDED.total_tokens;
```

### Materialized Views

```sql
CREATE MATERIALIZED VIEW mv_monthly_stats AS
SELECT
    DATE_TRUNC('month', created_at) as month,
    model,
    COUNT(*) as requests,
    SUM(tokens) as tokens,
    SUM(cost_usd) as cost
FROM fact_llm_requests
GROUP BY DATE_TRUNC('month', created_at), model;

-- Refresh
REFRESH MATERIALIZED VIEW mv_monthly_stats;
```

---

## Summary

1. **OLAP** — Analytics-optimized design
2. **Star schema** — Facts + dimensions
3. **SCD** — Track historical changes
4. **Partitioning** — Scale large tables
5. **Aggregates** — Pre-compute for speed
