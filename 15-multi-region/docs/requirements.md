# Requirements

## Functional

Route by region; replicate events; fail over; reconcile conflicting writes; restore backups.

## Non-functional

Every failure drill reports measured recovery time and observed data loss.

## Explicitly excluded

Real cloud regions, production DNS, formal consensus implementation.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.