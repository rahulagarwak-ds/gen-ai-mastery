# Workout: Data Warehousing

## Drill 1: Time Dimension 🟡

```sql
-- Create dim_time with date, week, month, quarter, year
```

## Drill 2: User Dimension 🟡

```sql
-- Create dim_user with SCD Type 2 fields
```

## Drill 3: Fact Table 🟡

```sql
-- Create fact_llm_requests with dimension keys and measures
```

## Drill 4: SCD Type 2 Update 🔴

```sql
-- Close old record and insert new for changed user
```

## Drill 5: Range Partition 🟡

```sql
-- Create partitioned table by month
```

## Drill 6: Materialized View 🟡

```sql
-- Create and refresh monthly stats view
```

## Drill 7: Aggregate Table 🔴

```sql
-- Create daily aggregates with upsert refresh
```

## Drill 8: Star Schema Query 🔴

```sql
-- Join fact to dimensions for monthly report
```

---

## Self-Check

- [ ] Can design star schema
- [ ] Can implement SCD Type 2
- [ ] Can create partitions
- [ ] Can use materialized views
