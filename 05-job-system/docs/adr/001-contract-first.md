# ADR 001: Begin with an executable contract shell

## Context

The project must be understandable before its distributed infrastructure is
introduced.

## Decision

Start with a runnable FastAPI boundary, standard health probes, request IDs,
and typed errors. Implement domain behavior in roadmap order.

## Alternatives

- Generate the complete distributed stack immediately.
- Keep documentation only with no executable contract.

## Consequences

The interface is testable now, while project-specific behavior correctly
remains marked planned. No placeholder metric can be mistaken for evidence.

## Rollback plan

Delete the shell when the real entrypoint replaces it; retain the public
health and error contracts.