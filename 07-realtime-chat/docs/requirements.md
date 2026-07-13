# Requirements

## Functional

Direct and group chat; message history; presence; read receipts; offline delivery.

## Non-functional

Messages are ordered within a conversation and acknowledged only after persistence.

## Explicitly excluded

End-to-end encryption, media calls, message search.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.