---
type: API Contract
title: API Rate Limits
description: Per-minute and per-day request limits for the public Northwind API.
owner: team:platform-api
last_reviewed: 2026-08-30
tags: [api, limits, quotas]
status: stable
---
# Limits

- **Per minute:** 600 requests per workspace, across all endpoints.
- **Per day:** depends on the plan. See [Pricing Tiers](/pricing/pricing-tiers.md)
  (Starter: no API access, Growth: 10,000 calls/day, Enterprise: 100,000 calls/day).

# When a limit is exceeded

The API returns `429 Too Many Requests` with a `Retry-After` header (seconds).
Daily quotas reset at 00:00 UTC.
