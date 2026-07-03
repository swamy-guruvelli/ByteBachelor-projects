import argparse
from uuid import uuid4

from sqlalchemy import insert

from app.database import SessionLocal
from app.models import Project, Task, User


def seed(task_count: int, batch_size: int) -> None:
    user_id = uuid4()
    project_id = uuid4()
    with SessionLocal.begin() as session:
        session.add(
            User(
                id=user_id,
                email=f"benchmark-{user_id}@example.com",
                display_name="Pagination benchmark",
            )
        )
        session.add(Project(id=project_id, owner_id=user_id, name="Benchmark"))

    with SessionLocal() as session:
        for start in range(0, task_count, batch_size):
            rows = [
                {
                    "id": uuid4(),
                    "project_id": project_id,
                    "title": f"Generated task {number}",
                    "description": None,
                    "status": "todo" if number % 3 else "done",
                    "due_at": None,
                    "version": 1,
                }
                for number in range(start, min(start + batch_size, task_count))
            ]
            session.execute(insert(Task), rows)
            session.commit()
            print(f"inserted {min(start + batch_size, task_count):,}/{task_count:,}")

    print(f"\nPROJECT_ID={project_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=int, default=100_000)
    parser.add_argument("--batch-size", type=int, default=5_000)
    arguments = parser.parse_args()
    seed(arguments.tasks, arguments.batch_size)

