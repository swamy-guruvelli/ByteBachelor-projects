import argparse
import statistics
from time import perf_counter
from uuid import UUID

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Task


def timed(session, statement, repeats: int) -> tuple[float, float]:
    samples = []
    for _ in range(repeats):
        started = perf_counter()
        list(session.scalars(statement))
        samples.append((perf_counter() - started) * 1_000)
    return statistics.median(samples), max(samples)


def benchmark(project_id: UUID, offset: int, limit: int, repeats: int) -> None:
    order = (Task.created_at.desc(), Task.id.desc())
    offset_query = (
        select(Task.id)
        .where(Task.project_id == project_id)
        .order_by(*order)
        .offset(offset)
        .limit(limit)
    )

    with SessionLocal() as session:
        pivot = session.execute(
            select(Task.created_at, Task.id)
            .where(Task.project_id == project_id)
            .order_by(*order)
            .offset(offset)
            .limit(1)
        ).one()
        cursor_query = (
            select(Task.id)
            .where(
                Task.project_id == project_id,
                (Task.created_at < pivot.created_at)
                | ((Task.created_at == pivot.created_at) & (Task.id <= pivot.id)),
            )
            .order_by(*order)
            .limit(limit)
        )
        offset_median, offset_max = timed(session, offset_query, repeats)
        cursor_median, cursor_max = timed(session, cursor_query, repeats)

    print(f"offset median={offset_median:.2f}ms max={offset_max:.2f}ms")
    print(f"cursor median={cursor_median:.2f}ms max={cursor_max:.2f}ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id", type=UUID)
    parser.add_argument("--offset", type=int, default=50_000)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--repeats", type=int, default=20)
    args = parser.parse_args()
    benchmark(args.project_id, args.offset, args.limit, args.repeats)

