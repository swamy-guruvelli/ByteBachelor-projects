# Requirements

## Functional

Accept notification events; honor preferences; render templates; deliver mock channels; collect receipts.

## Non-functional

The same event, recipient, and channel combination produces at most one delivery.

## Explicitly excluded

Real SMS/email vendors, marketing campaigns, template editor.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.