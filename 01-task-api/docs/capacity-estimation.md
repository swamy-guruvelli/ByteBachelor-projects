# Capacity estimation

Baseline assumptions:

- 10,000 active users.
- 20 projects and 200 tasks per user: 2 million tasks.
- 100 average and 1,000 peak requests/second.
- 80% reads and 20% writes.
- Roughly 1 KiB per task including indexes and row overhead: about 2 GiB.

At 1,000 peak requests/second and 50 ms average database time, Little's Law
suggests roughly 50 concurrent database operations. The default 15-connection
per-instance ceiling therefore limits safe API replica count; it is a deliberate
knob to test rather than a claim that more connections always improve throughput.

Measure row size, query latency, and pool wait time before replacing these
assumptions.

