# Load-test results

## Acceptance suite

The local SQLite-backed API suite is the fast correctness check. The same suite
runs against PostgreSQL through `docker-compose.test.yml`.

## Performance run

Not measured in this environment yet. Run:

```bash
locust -f loadtest/locustfile.py --host http://localhost:8000
```

Record real values only:

| Dataset | Mode | Throughput | P50 | P95 | P99 | Errors |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 100k tasks | Cursor | pending | pending | pending | pending | pending |
| 100k tasks | Offset 10k | pending | pending | pending | pending | pending |
| 1m tasks | Cursor | pending | pending | pending | pending | pending |
| 1m tasks | Offset 100k | pending | pending | pending | pending | pending |

