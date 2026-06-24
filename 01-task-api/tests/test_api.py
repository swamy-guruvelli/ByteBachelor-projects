from datetime import UTC, datetime, timedelta
from uuid import uuid4


def create_workspace(client):
    user = client.post(
        "/api/v1/users",
        json={"email": "learner@example.com", "display_name": "System Learner"},
    ).json()
    project = client.post(
        "/api/v1/projects",
        json={"owner_id": user["id"], "name": "Build the lab"},
    ).json()
    label = client.post(
        "/api/v1/labels",
        json={"owner_id": user["id"], "name": "architecture", "color": "#ea580c"},
    ).json()
    return user, project, label


def test_health_and_request_id(client):
    response = client.get("/health/ready", headers={"X-Request-ID": "trace-the-request"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "trace-the-request"
    assert response.json() == {"status": "ready", "database": "reachable"}


def test_problem_contract_covers_validation_and_missing_routes(client):
    validation = client.post("/api/v1/users", json={"email": "not-an-email"})
    missing = client.get("/does-not-exist")
    assert validation.status_code == 422
    assert validation.headers["content-type"].startswith("application/problem+json")
    assert validation.json()["type"].endswith("validation")
    assert missing.status_code == 404
    assert missing.json()["type"].endswith("http-404")


def test_user_project_and_label_crud(client):
    user, project, label = create_workspace(client)

    changed_user = client.patch(
        f"/api/v1/users/{user['id']}", json={"display_name": "Architecture Learner"}
    )
    changed_project = client.patch(
        f"/api/v1/projects/{project['id']}", json={"description": "Fifteen systems"}
    )
    changed_label = client.patch(
        f"/api/v1/labels/{label['id']}", json={"color": "#0f766e"}
    )

    assert changed_user.json()["display_name"] == "Architecture Learner"
    assert changed_project.json()["description"] == "Fifteen systems"
    assert changed_label.json()["color"] == "#0f766e"
    assert len(client.get(f"/api/v1/projects?owner_id={user['id']}").json()) == 1


def test_unique_constraints_return_conflicts(client):
    user, project, label = create_workspace(client)
    duplicate_user = client.post(
        "/api/v1/users",
        json={"email": user["email"], "display_name": "Duplicate"},
    )
    duplicate_project = client.post(
        "/api/v1/projects",
        json={"owner_id": user["id"], "name": project["name"]},
    )
    duplicate_label = client.post(
        "/api/v1/labels",
        json={"owner_id": user["id"], "name": label["name"], "color": "#123456"},
    )
    responses = (duplicate_user, duplicate_project, duplicate_label)
    assert [response.status_code for response in responses] == [
        409,
        409,
        409,
    ]


def test_task_crud_and_label_ownership(client):
    user, project, label = create_workspace(client)
    task = client.post(
        "/api/v1/tasks",
        json={
            "project_id": project["id"],
            "title": "Model the data",
            "due_at": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
            "label_ids": [label["id"]],
        },
    )
    assert task.status_code == 201
    assert task.json()["labels"][0]["name"] == "architecture"

    other_user = client.post(
        "/api/v1/users",
        json={"email": "other@example.com", "display_name": "Other"},
    ).json()
    other_label = client.post(
        "/api/v1/labels",
        json={"owner_id": other_user["id"], "name": "private", "color": "#123456"},
    ).json()
    invalid = client.post(
        "/api/v1/tasks",
        json={
            "project_id": project["id"],
            "title": "Cross owner",
            "label_ids": [other_label["id"]],
        },
    )
    assert invalid.status_code == 422
    assert invalid.json()["type"].endswith("invalid-labels")


def test_optimistic_locking_rejects_stale_updates(client):
    _, project, _ = create_workspace(client)
    task = client.post(
        "/api/v1/tasks",
        json={"project_id": project["id"], "title": "Version one"},
    ).json()

    first = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"version": 1, "title": "Version two"},
    )
    stale = client.patch(
        f"/api/v1/tasks/{task['id']}",
        json={"version": 1, "title": "Lost update"},
    )
    assert first.status_code == 200
    assert first.json()["version"] == 2
    assert stale.status_code == 409
    assert stale.json()["type"].endswith("version-conflict")


def test_offset_and_cursor_pagination_return_the_same_collection(client):
    _, project, _ = create_workspace(client)
    created_ids = {
        client.post(
            "/api/v1/tasks",
            json={"project_id": project["id"], "title": f"Task {number}"},
        ).json()["id"]
        for number in range(5)
    }
    offset_ids = {
        item["id"]
        for page_offset in (0, 2, 4)
        for item in client.get(f"/api/v1/tasks?limit=2&offset={page_offset}").json()["items"]
    }

    cursor_ids = set()
    cursor = None
    while True:
        query = "/api/v1/tasks?limit=2" + (f"&cursor={cursor}" if cursor else "")
        page = client.get(query).json()
        cursor_ids.update(item["id"] for item in page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            break

    assert offset_ids == created_ids
    assert cursor_ids == created_ids


def test_filters_and_versioned_delete(client):
    _, project, label = create_workspace(client)
    todo = client.post(
        "/api/v1/tasks",
        json={
            "project_id": project["id"],
            "title": "Todo",
            "label_ids": [label["id"]],
        },
    ).json()
    client.post(
        "/api/v1/tasks",
        json={"project_id": project["id"], "title": "Done", "status": "done"},
    )

    filtered = client.get(
        f"/api/v1/tasks?project_id={project['id']}&status=todo&label_id={label['id']}"
    )
    stale_delete = client.delete(f"/api/v1/tasks/{todo['id']}?version=2")
    deleted = client.delete(f"/api/v1/tasks/{todo['id']}?version=1")
    assert filtered.json()["total"] == 1
    assert stale_delete.status_code == 409
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/tasks/{uuid4()}").status_code == 404
