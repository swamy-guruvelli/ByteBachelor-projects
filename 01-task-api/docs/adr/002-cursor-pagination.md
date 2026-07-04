# ADR 002: Offer cursor and offset pagination

## Context

Learners need to observe both the simplicity of offsets and the stable
performance of keyset cursors.

## Decision

Expose both modes but reject requests that mix them. Cursor ordering is
`created_at DESC, id DESC`.

## Alternatives

Offset-only is simpler but degrades on deep pages. Cursor-only prevents direct
page jumps and hides an important comparison.

## Consequences

Clients must treat cursors as opaque. The database needs a matching composite
index and deterministic tie-breaker.

## Rollback

Remove offset mode if measured production traffic never needs page jumps.

