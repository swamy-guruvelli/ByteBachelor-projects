# Requirements

## Functional

Compute one-minute metrics; handle late events; serve dashboard data; replay; backfill; reconcile daily.

## Non-functional

Every output identifies its input window and can be deterministically rebuilt.

## Explicitly excluded

Managed lakehouse, arbitrary SQL engine, ML feature serving.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.