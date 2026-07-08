# Requirements

## Functional

Apply per-route policies; emit 429 responses and standard headers; identify callers by user, IP, or key.

## Non-functional

No accepted request may exceed a fail-closed policy under concurrent load.

## Explicitly excluded

Billing quotas, WAF rules, global traffic management.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.