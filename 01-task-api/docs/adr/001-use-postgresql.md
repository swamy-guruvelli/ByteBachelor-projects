# ADR 001: Use PostgreSQL as the system of record

## Context

Users, projects, tasks, and labels have relational constraints and transactional
updates.

## Decision

Use PostgreSQL with foreign keys, uniqueness, checks, and composite indexes.

## Alternatives

SQLite is useful for the fast test loop but does not model production
concurrency. A document database would move relational integrity into code.

## Consequences

The schema can enforce ownership relationships and optimistic versions. The
service must operate a connection pool and migrations.

## Rollback

Export the small relational dataset as JSON only if requirements become
document-shaped and cross-record transactions disappear.

