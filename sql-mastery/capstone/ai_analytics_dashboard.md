# 🏆 Capstone: AI Analytics Dashboard Schema

## 🎯 Objective

Design a complete data warehouse schema for LLM usage analytics.

---

## 📋 Requirements

### 1. Dimensions

```sql
-- dim_time: Date, week, month, quarter, year, is_weekend
-- dim_user: User info with SCD Type 2
-- dim_model: Model, provider, pricing
-- dim_session: Session metadata
```

### 2. Fact Tables

```sql
-- fact_requests: Every LLM API call
--   - Dimensions: time, user, model, session
--   - Measures: input_tokens, output_tokens, latency_ms, cost_usd

-- fact_retrieval: Every RAG retrieval
--   - Measures: chunks_retrieved, avg_similarity, latency_ms
```

### 3. Aggregates

```sql
-- agg_daily_usage: Daily rollup by user
-- agg_model_performance: Model-level metrics
```

### 4. Required Queries

```sql
-- Q1: Monthly cost by model
-- Q2: User retention (D1, D7, D30)
-- Q3: Token usage trend
-- Q4: Model latency percentiles
-- Q5: Top users by cost
```

---

## ✅ Deliverables

1. **Schema DDL** — All CREATE TABLE statements
2. **Indexes** — Performance optimization
3. **Sample ETL** — Load from source to warehouse
4. **Dashboard queries** — 5 analytics queries
5. **Materialized views** — Pre-computed summaries

**Time estimate:** 3-4 hours
