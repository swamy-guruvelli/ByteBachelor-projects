# 08. Search and Autocomplete

> Status: **planned contract shell** — the learning specification and service
> boundary are runnable; domain behavior is implemented in roadmap order.

The same search contract backed first by PostgreSQL and then OpenSearch.

## How it works

```mermaid
flowchart LR
    Client --> API[FastAPI contract]
    API -. implementation milestone .-> Domain[Project behavior]
```

The baseline deliberately starts with the fewest components that can expose
the design question. Infrastructure is added only when an experiment proves
the need.

## Try it

```bash
docker compose up --build
curl http://localhost:8000/health/ready
curl -i http://localhost:8000/api/v1/planned
```

The second request returns a typed 501 application/problem+json response so
consumers can integrate against the common service contract without mistaking
this milestone for a finished implementation.

## Break it

Measure relevance and latency as corpus size grows; document the PostgreSQL crossover point.

## Learning target

Inverted indexes, tokenization, ranking, indexing pipelines, reindexing, eventual consistency.

See docs/system-design.md for the implementation boundary and sequence.