# Requirements

## Functional

Submit email, report, and image jobs; inspect state; retry transient errors; quarantine poison jobs.

## Non-functional

A duplicated message causes at most one recorded side effect.

## Explicitly excluded

Cron scheduling, arbitrary user code, multi-tenant billing.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.