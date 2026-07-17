# Requirements

## Functional

Register and sign in; rotate and revoke refresh tokens; enforce roles; route requests; audit decisions.

## Non-functional

Revoked credentials cannot be refreshed; passwords and secrets never appear in logs.

## Explicitly excluded

External OAuth providers, enterprise SSO, dynamic service discovery.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.