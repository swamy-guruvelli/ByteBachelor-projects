# Requirements

## Functional

- Create, read, update, list, and delete users, projects, labels, and tasks.
- Keep projects and labels owned by users and tasks contained in projects.
- Assign only the project owner's labels to a task.
- Filter tasks by project, status, label, and due date.
- Page tasks with either an offset or an opaque cursor.
- Reject lost updates using a task version.

## Non-functional

- Baseline availability target: 99.9%.
- Baseline P95 API latency target: below 200 ms at 100 requests/second.
- Every error follows `application/problem+json`.
- Every response carries a request ID.
- Queries are bounded to at most 100 resources per page.
- Database connections use a bounded pool and are returned after every request.

## Explicitly excluded

- Authentication and authorization; those are introduced in Project 10.
- Redis, queues, microservices, and Kubernetes.
- Task attachments, recurring tasks, comments, and notifications.

