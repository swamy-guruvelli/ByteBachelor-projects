# ADR 003: Use optimistic task locking

## Context

Task edits are short and contention is normally low, but silent lost updates
are unacceptable.

## Decision

Require the observed integer version on PATCH and DELETE. Update atomically
where ID and version match.

## Alternatives

Pessimistic row locks hold scarce connections while clients think. Last-write
wins silently discards work.

## Consequences

Clients must reload after `409`. High-conflict workloads may need a serialized
command queue, but that complexity is not justified here.

## Rollback

Move only demonstrated high-contention operations to pessimistic locking or a
queue.

