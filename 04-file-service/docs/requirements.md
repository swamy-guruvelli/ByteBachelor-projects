# Requirements

## Functional

Create uploads; stream small files; resume multipart uploads; verify checksums; issue secure downloads.

## Non-functional

API memory use stays bounded as file size grows; corrupt uploads are never marked complete.

## Explicitly excluded

Virus scanning, media transcoding, public CDN.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.