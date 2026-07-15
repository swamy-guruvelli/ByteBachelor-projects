# Requirements

## Functional

Index documents; full-text search; prefix suggestions; typo-tolerant dedicated search; reindex.

## Non-functional

Search remains queryable during a versioned index rebuild.

## Explicitly excluded

Semantic vector search, personalization, web crawling.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.