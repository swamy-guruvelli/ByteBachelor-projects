# Failure analysis

Primary drills: Payment timeout, inventory race, duplicate event, compensation failure.

For each drill record:

1. User-visible behavior and status code.
2. Whether retry is safe and which idempotency key protects it.
3. Data that can be duplicated, reordered, delayed, or lost.
4. Backpressure point and recovery action.
5. Metric or alert that detects the fault.