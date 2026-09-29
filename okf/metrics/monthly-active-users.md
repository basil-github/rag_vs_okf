---
type: Metric
title: Monthly Active Users (MAU)
description: Official definition of Monthly Active Users, Northwind's primary engagement metric.
owner: team:growth-analytics
last_reviewed: 2026-08-12
tags: [metrics, engagement, mau, north-star]
status: stable
stale_after: 2027-02-28
verified:
  - by: human:priya.raman
    at: 2026-08-12T10:00:00Z
---
# Definition

**Monthly Active Users (MAU)** is the number of **distinct users** who performed at least one
**qualifying action** in the **trailing 28 days** (rolling window, UTC).

Qualifying actions:

- running a query
- viewing a dashboard for at least 10 seconds
- creating or editing a report

# Exclusions

- Internal Northwind accounts (`@northwind-analytics.com`)
- Test and sandbox workspaces
- API-only service accounts (tracked separately as "API clients")

# History

This definition took effect on **2026-03-01**. The previous definition, "any user who logged in
at least once during the calendar month", is **deprecated**. It counted users who logged in and
left immediately, and calendar months of different lengths made month-over-month comparisons uneven.

# Computation

```sql
SELECT COUNT(DISTINCT user_id) AS mau
FROM events.qualifying_actions
WHERE event_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 28 DAY)
  AND is_internal = FALSE
  AND is_test_workspace = FALSE
  AND account_kind != 'service';
```

# Related

- Owned by Growth Analytics, see [Team Ownership](/teams/team-ownership.md)
- Feeds [Activation Rate](/metrics/activation-rate.md)
