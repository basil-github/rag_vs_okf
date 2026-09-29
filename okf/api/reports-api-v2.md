---
type: API Contract
title: Reports API v2
description: Contract for the Reports API v2, including endpoints and every response field.
owner: team:platform-api
last_reviewed: 2026-08-30
tags: [api, reports, contract, v2]
status: stable
resource: https://api.northwind-analytics.example/v2/reports
verified:
  - by: human:marcus.okafor
    at: 2026-08-30T15:00:00Z
---
# Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/v2/reports` | List reports in the workspace (paginated, 50 per page) |
| GET | `/v2/reports/{report_id}` | Get a single report |
| POST | `/v2/reports/{report_id}/refresh` | Trigger a refresh (async, returns 202) |

Authentication: `Authorization: Bearer <api_token>`. Limits: see [API Rate Limits](/api/rate-limits.md).

# Schema

Response fields for `GET /v2/reports/{report_id}`:

| Field | Type | Description |
|---|---|---|
| `report_id` | string | Unique report ID, e.g. `rpt_8f2a91` |
| `workspace_id` | string | Owning [workspace](/glossary/workspace.md) |
| `name` | string | Display name |
| `status` | enum | `ready`, `refreshing` or `failed` |
| `refresh_interval_minutes` | integer | Scheduled refresh interval in minutes; `null` if manual only |
| `last_refreshed_at` | string | Time of the last successful refresh, **ISO 8601 timestamp in UTC** (e.g. `2026-09-01T08:30:00Z`) |
| `owner_email` | string | Email of the report owner |
| `created_at` | string | ISO 8601 UTC creation time |

# Changes from v1

- `refresh_rate` (v1, a string like `"1h"`) was **removed** and replaced by `refresh_interval_minutes` (integer).
- `last_updated` (v1, local-time string) was **removed** and replaced by `last_refreshed_at` (ISO 8601, UTC).
- v1 is deprecated and will be shut down on 2026-12-31.

# Examples

```json
{
  "report_id": "rpt_8f2a91",
  "workspace_id": "ws_4410",
  "name": "Weekly revenue",
  "status": "ready",
  "refresh_interval_minutes": 60,
  "last_refreshed_at": "2026-09-01T08:30:00Z",
  "owner_email": "ana@example.com",
  "created_at": "2026-02-11T12:00:00Z"
}
```
