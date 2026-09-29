---
type: Playbook
title: Dashboard Outage Runbook
description: On-call steps when customer dashboards fail to load or time out.
owner: team:sre
last_reviewed: 2026-07-28
tags: [runbook, on-call, incident, dashboards]
status: stable
---
# Trigger

PagerDuty alert `dashboards-p95-latency > 8s for 10 min` or `dashboard-error-rate > 2%`.

# Steps

1. **Acknowledge** the page within 5 minutes (rotation: `nw-platform-primary`).
2. Open the *Dashboards Health* Grafana board. Check query-engine CPU and the Redis cache hit rate.
3. If the cache hit rate < 60%: restart the `cache-warmer` job (`kubectl rollout restart deploy/cache-warmer -n dash`).
4. If one workspace dominates load, apply the per-workspace query throttle (`nwctl throttle --workspace <id> --qps 5`).
5. Post status in `#incidents` every 30 minutes; update the public status page for SEV1/SEV2.

# Escalation

- No acknowledgement in 15 min → secondary on-call (`nw-platform-secondary`).
- Not mitigated in 45 min → SRE lead (see [Team Ownership](/teams/team-ownership.md)).

# Severity

- **SEV1**: all customers affected. **SEV2**: one region or >10% of workspaces. **SEV3**: a single customer.
