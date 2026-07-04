# Failure analysis

| Failure | User-visible behavior | Guarantee |
| --- | --- | --- |
| PostgreSQL unavailable | Readiness and data requests fail; orchestrator stops routing | No false readiness |
| Duplicate create | Unique constraint returns 409 | No duplicate email/name |
| Concurrent task update | One succeeds, stale version returns 409 | No silent lost update |
| Invalid cross-owner label | 422 before insert | Ownership boundary preserved |
| Malformed cursor | 400 problem response | No accidental full scan |
| Client retries GET | Safe | No state change |
| Client retries PATCH after timeout | Version determines whether it already committed | No second update from same version |

The service does not retry database writes automatically because the client must
know whether a versioned operation is safe to repeat.

