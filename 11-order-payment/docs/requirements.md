# Requirements

## Functional

Create order; reserve stock; authorize mock payment; confirm; request shipment; compensate failures.

## Non-functional

Retries never double-charge and failed checkout releases every acquired resource.

## Explicitly excluded

Real payment provider, catalog UI, warehouse optimization.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.