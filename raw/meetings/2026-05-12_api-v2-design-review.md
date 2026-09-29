# Reports API v2 — design review — 2026-05-12

Attendees: Marcus Okafor (Platform API lead), Leo Park, Nadia K., Tomás Ibarra

## Decisions
- Rename `refresh_rate` (string "1h") → `refresh_interval_minutes` (integer).
- Replace `last_updated` (local time string, source of many tz bugs) with `last_refreshed_at` in UTC.
- Add `status` enum: ready / refreshing / failed.
- Keep 600 req/min per workspace limit.

## Parking lot
- `next_refresh_at` field (customer ask), maybe v2.1
- Webhooks on refresh complete
