# Chapter 3: Analytics SQL — Product Intelligence

> _"Data-driven decisions require data-savvy queries."_

---

## What You'll Learn

- Cohort analysis
- Funnel analysis
- Retention metrics
- User segmentation
- A/B test analysis

---

## 1. Cohort Analysis

### User Cohorts by Sign-up Month

```sql
WITH cohorts AS (
    SELECT
        id,
        DATE_TRUNC('month', created_at) as cohort_month
    FROM users
),
activity AS (
    SELECT
        user_id,
        DATE_TRUNC('month', created_at) as activity_month
    FROM events
)
SELECT
    c.cohort_month,
    a.activity_month,
    COUNT(DISTINCT c.id) as users,
    a.activity_month - c.cohort_month as months_since_signup
FROM cohorts c
JOIN activity a ON c.id = a.user_id
GROUP BY c.cohort_month, a.activity_month
ORDER BY c.cohort_month, a.activity_month;
```

### Cohort Retention Table

```sql
WITH cohorts AS (
    SELECT
        user_id,
        MIN(DATE_TRUNC('week', created_at)) as cohort_week
    FROM user_sessions
    GROUP BY user_id
),
activity AS (
    SELECT
        user_id,
        DATE_TRUNC('week', created_at) as activity_week
    FROM user_sessions
)
SELECT
    cohort_week,
    (activity_week - cohort_week)::int / 7 as week_number,
    COUNT(DISTINCT a.user_id)::float /
        NULLIF(MAX(COUNT(DISTINCT a.user_id)) OVER (PARTITION BY cohort_week), 0) as retention_rate
FROM cohorts c
JOIN activity a ON c.user_id = a.user_id
GROUP BY cohort_week, week_number
ORDER BY cohort_week, week_number;
```

---

## 2. Funnel Analysis

### Basic Funnel

```sql
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'page_view' THEN 1 END) as viewed,
        MAX(CASE WHEN event = 'signup_start' THEN 1 END) as started_signup,
        MAX(CASE WHEN event = 'signup_complete' THEN 1 END) as completed_signup,
        MAX(CASE WHEN event = 'first_chat' THEN 1 END) as first_chat
    FROM events
    WHERE created_at > NOW() - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT
    COUNT(*) FILTER (WHERE viewed = 1) as step_1_views,
    COUNT(*) FILTER (WHERE started_signup = 1) as step_2_started,
    COUNT(*) FILTER (WHERE completed_signup = 1) as step_3_completed,
    COUNT(*) FILTER (WHERE first_chat = 1) as step_4_chat,
    ROUND(100.0 * COUNT(*) FILTER (WHERE started_signup = 1) /
        NULLIF(COUNT(*) FILTER (WHERE viewed = 1), 0), 1) as step_1_to_2_rate,
    ROUND(100.0 * COUNT(*) FILTER (WHERE first_chat = 1) /
        NULLIF(COUNT(*) FILTER (WHERE viewed = 1), 0), 1) as overall_conversion
FROM funnel;
```

### Time-Ordered Funnel

```sql
WITH ordered_events AS (
    SELECT
        user_id,
        event,
        created_at,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) as event_order
    FROM events
    WHERE event IN ('view', 'add_to_cart', 'checkout', 'purchase')
)
SELECT
    user_id,
    MAX(CASE WHEN event = 'view' THEN created_at END) as viewed_at,
    MAX(CASE WHEN event = 'purchase' THEN created_at END) as purchased_at,
    EXTRACT(EPOCH FROM (
        MAX(CASE WHEN event = 'purchase' THEN created_at END) -
        MAX(CASE WHEN event = 'view' THEN created_at END)
    )) / 3600 as hours_to_purchase
FROM ordered_events
GROUP BY user_id;
```

---

## 3. Retention Metrics

### Day-N Retention

```sql
WITH first_day AS (
    SELECT
        user_id,
        DATE(MIN(created_at)) as first_active
    FROM user_sessions
    GROUP BY user_id
),
retention AS (
    SELECT
        f.first_active,
        s.user_id,
        DATE(s.created_at) - f.first_active as day_n
    FROM first_day f
    JOIN user_sessions s ON f.user_id = s.user_id
)
SELECT
    first_active,
    COUNT(DISTINCT user_id) FILTER (WHERE day_n = 0) as d0,
    COUNT(DISTINCT user_id) FILTER (WHERE day_n = 1) as d1,
    COUNT(DISTINCT user_id) FILTER (WHERE day_n = 7) as d7,
    COUNT(DISTINCT user_id) FILTER (WHERE day_n = 30) as d30,
    ROUND(100.0 * COUNT(DISTINCT user_id) FILTER (WHERE day_n = 7) /
        NULLIF(COUNT(DISTINCT user_id) FILTER (WHERE day_n = 0), 0), 1) as d7_retention
FROM retention
GROUP BY first_active
ORDER BY first_active DESC;
```

---

## 4. LLM Usage Analytics

### Token Usage by User

```sql
SELECT
    user_id,
    DATE_TRUNC('day', created_at) as day,
    SUM(input_tokens) as total_input,
    SUM(output_tokens) as total_output,
    SUM(input_tokens + output_tokens) as total_tokens,
    COUNT(*) as request_count,
    ROUND(AVG(input_tokens + output_tokens), 0) as avg_tokens_per_request
FROM llm_requests
GROUP BY user_id, DATE_TRUNC('day', created_at)
ORDER BY day DESC;
```

### Model Performance Comparison

```sql
SELECT
    model,
    COUNT(*) as requests,
    ROUND(AVG(latency_ms), 0) as avg_latency,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
    SUM(cost_usd) as total_cost,
    ROUND(AVG(cost_usd), 4) as avg_cost_per_request
FROM llm_requests
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY model
ORDER BY requests DESC;
```

---

## 5. A/B Test Analysis

### Variant Comparison

```sql
WITH experiment_data AS (
    SELECT
        e.user_id,
        e.variant,
        COUNT(c.id) as conversions,
        SUM(c.amount) as revenue
    FROM experiment_assignments e
    LEFT JOIN conversions c ON e.user_id = c.user_id
        AND c.created_at BETWEEN e.assigned_at AND e.assigned_at + INTERVAL '7 days'
    WHERE e.experiment = 'new_onboarding'
    GROUP BY e.user_id, e.variant
)
SELECT
    variant,
    COUNT(*) as users,
    SUM(conversions) as total_conversions,
    ROUND(100.0 * SUM(CASE WHEN conversions > 0 THEN 1 END) / COUNT(*), 2) as conversion_rate,
    ROUND(AVG(revenue), 2) as avg_revenue_per_user
FROM experiment_data
GROUP BY variant;
```

---

## Summary

1. **Cohorts** — Group users by signup time
2. **Funnels** — Track conversion steps
3. **Retention** — D1, D7, D30 metrics
4. **LLM analytics** — Token, cost, latency
5. **A/B tests** — Statistical comparisons
