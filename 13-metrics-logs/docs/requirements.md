# Requirements

## Functional

Ingest tenant events; batch and partition; query recent data; archive Parquet; build hourly aggregates.

## Non-functional

Overload is bounded by explicit backpressure rather than unbounded memory growth.

## Explicitly excluded

Alerting engine, dashboards, proprietary agents.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.