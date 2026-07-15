# Requirements

## Functional

Follow users; publish posts; read ranked timelines; switch fan-out strategy.

## Non-functional

Feed pagination is stable while new posts arrive.

## Explicitly excluded

Ads, recommendation ML, media uploads.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.