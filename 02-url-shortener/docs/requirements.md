# Requirements

## Functional

Create generated or custom aliases; redirect active links; expire links; record click counts.

## Non-functional

P95 redirect latency below 50 ms at the baseline load; redirects remain available when Redis is down.

## Explicitly excluded

Custom domains, abuse detection, geographic analytics.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.