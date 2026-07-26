# Requirements

## Functional

Enter queue; reserve seat; expire hold; confirm payment; release reservation.

## Non-functional

Confirmed tickets plus active reservations never exceeds venue capacity.

## Explicitly excluded

Seat maps, resale, dynamic pricing.

## Completion evidence

- API and event contracts are executable.
- The named experiment records throughput and P50/P95/P99 latency.
- Failure behavior is reproduced and documented.
- Architecture decisions include an upgrade signal and rollback path.