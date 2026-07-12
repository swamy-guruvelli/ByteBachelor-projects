# 06. Notification Platform

> Status: **planned contract shell** — the learning specification and service
> boundary are runnable; domain behavior is implemented in roadmap order.

Multi-channel delivery with preferences, fan-out, receipts, and provider controls.

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

Throttle one provider; replay a duplicate event; return delayed webhook receipts.

## Learning target

Routing, templates, fan-out, provider abstraction, deduplication, receipts.

See docs/system-design.md for the implementation boundary and sequence.