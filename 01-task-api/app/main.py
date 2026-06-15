import base64
import json
import logging
import os
from datetime import datetime
from time import perf_counter
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import and_, delete, func, or_, select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import get_db
from app.errors import ProblemError
from app.models import Label, Project, Task, User
from app.schemas import (
    LabelCreate,
    LabelRead,
    LabelUpdate,
    Problem,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    TaskCreate,
    TaskPage,
    TaskRead,
    TaskUpdate,
    UserCreate,
    UserRead,
    UserUpdate,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(message)s",
)
logger = logging.getLogger("task-api")

app = FastAPI(
    title="System Design Lab — Task API",
    version="1.0.0",
    description=(
        "A learning-first REST API demonstrating relational modeling, pagination, "
        "indexes, optimistic locking, and connection pooling."
    ),
    responses={
        400: {"model": Problem},
        404: {"model": Problem},
        409: {"model": Problem},
        422: {"model": Problem},
    },
)


def problem_response(
    request: Request,
    status_code: int,
    title: str,
    detail: str,
    code: str,
    errors: list[dict] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content=jsonable_encoder(
            {
                "type": f"urn:system-design-lab:problem:{code}",
                "title": title,
                "status": status_code,
                "detail": detail,
                "instance": request.url.path,
                "errors": errors,
            },
            exclude_none=True,
        ),
    )


@app.exception_handler(ProblemError)
async def handle_problem(request: Request, error: ProblemError) -> JSONResponse:
    return problem_response(
        request,
        error.status,
        error.title,
        error.detail,
        error.code,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation(request: Request, error: RequestValidationError) -> JSONResponse:
    return problem_response(
        request,
        422,
        "Request validation failed",
        "One or more request values are invalid.",
        "validation",
        jsonable_encoder(error.errors()),
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(request: Request, error: StarletteHTTPException) -> JSONResponse:
    title = "Resource not found" if error.status_code == 404 else "HTTP request failed"
    return problem_response(
        request,
        error.status_code,
        title,
        str(error.detail),
        f"http-{error.status_code}",
    )


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        json.dumps(
            {
                "event": "request.completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            }
        )
    )
    return response


def not_found(kind: str, identifier: UUID) -> ProblemError:
    return ProblemError(
        404,
        f"{kind} not found",
        f"No {kind.lower()} exists with id {identifier}.",
        "not-found",
    )


def commit(db: Session, conflict_detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ProblemError(409, "Resource conflict", conflict_detail, "conflict") from error


def get_user(db: Session, user_id: UUID) -> User:
    user = db.get(User, user_id)
    if not user:
        raise not_found("User", user_id)
    return user


def get_project(db: Session, project_id: UUID) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise not_found("Project", project_id)
    return project


def get_task(db: Session, task_id: UUID) -> Task:
    task = db.scalar(
        select(Task).where(Task.id == task_id).options(selectinload(Task.labels))
    )
    if not task:
        raise not_found("Task", task_id)
    return task


def labels_for_owner(db: Session, label_ids: list[UUID], owner_id: UUID) -> list[Label]:
    unique_ids = list(dict.fromkeys(label_ids))
    if not unique_ids:
        return []
    labels = list(
        db.scalars(select(Label).where(Label.id.in_(unique_ids), Label.owner_id == owner_id))
    )
    if len(labels) != len(unique_ids):
        raise ProblemError(
            422,
            "Invalid labels",
            "Every label must exist and belong to the project owner.",
            "invalid-labels",
        )
    return labels


def encode_cursor(task: Task) -> str:
    raw = json.dumps(
        {"created_at": task.created_at.isoformat(), "id": str(task.id)},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        raw = base64.urlsafe_b64decode(cursor + "=" * (-len(cursor) % 4))
        value = json.loads(raw)
        return datetime.fromisoformat(value["created_at"]), UUID(value["id"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise ProblemError(
            400,
            "Invalid cursor",
            "The pagination cursor is malformed or incomplete.",
            "invalid-cursor",
        ) from error


@app.get("/health/live", tags=["health"])
def live() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["health"])
def ready(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as error:
        raise ProblemError(
            503,
            "Database unavailable",
            "The service cannot reach its primary database.",
            "database-unavailable",
        ) from error
    return {"status": "ready", "database": "reachable"}


@app.post("/api/v1/users", response_model=UserRead, status_code=201, tags=["users"])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(email=str(payload.email).lower(), display_name=payload.display_name)
    db.add(user)
    commit(db, "A user with that email already exists.")
    db.refresh(user)
    return user


@app.get("/api/v1/users", response_model=list[UserRead], tags=["users"])
def list_users(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[User]:
    query = select(User).order_by(User.created_at, User.id).limit(limit).offset(offset)
    return list(db.scalars(query))


@app.get("/api/v1/users/{user_id}", response_model=UserRead, tags=["users"])
def read_user(user_id: UUID, db: Session = Depends(get_db)) -> User:
    return get_user(db, user_id)


@app.patch("/api/v1/users/{user_id}", response_model=UserRead, tags=["users"])
def update_user(user_id: UUID, payload: UserUpdate, db: Session = Depends(get_db)) -> User:
    user = get_user(db, user_id)
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("email"):
        changes["email"] = str(changes["email"]).lower()
    for field, value in changes.items():
        setattr(user, field, value)
    commit(db, "A user with that email already exists.")
    db.refresh(user)
    return user


@app.delete("/api/v1/users/{user_id}", status_code=204, tags=["users"])
def delete_user(user_id: UUID, db: Session = Depends(get_db)) -> Response:
    db.delete(get_user(db, user_id))
    db.commit()
    return Response(status_code=204)


@app.post("/api/v1/projects", response_model=ProjectRead, status_code=201, tags=["projects"])
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    get_user(db, payload.owner_id)
    project = Project(**payload.model_dump())
    db.add(project)
    commit(db, "That owner already has a project with this name.")
    db.refresh(project)
    return project


@app.get("/api/v1/projects", response_model=list[ProjectRead], tags=["projects"])
def list_projects(
    owner_id: UUID | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[Project]:
    query = select(Project).order_by(Project.created_at, Project.id)
    if owner_id:
        query = query.where(Project.owner_id == owner_id)
    return list(db.scalars(query.limit(limit).offset(offset)))


@app.get("/api/v1/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
def read_project(project_id: UUID, db: Session = Depends(get_db)) -> Project:
    return get_project(db, project_id)


@app.patch("/api/v1/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
def update_project(
    project_id: UUID, payload: ProjectUpdate, db: Session = Depends(get_db)
) -> Project:
    project = get_project(db, project_id)
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("name", "valid") is None:
        raise ProblemError(422, "Invalid project", "Project name cannot be null.", "validation")
    for field, value in changes.items():
        setattr(project, field, value)
    commit(db, "That owner already has a project with this name.")
    db.refresh(project)
    return project


@app.delete("/api/v1/projects/{project_id}", status_code=204, tags=["projects"])
def delete_project(project_id: UUID, db: Session = Depends(get_db)) -> Response:
    db.delete(get_project(db, project_id))
    db.commit()
    return Response(status_code=204)


@app.post("/api/v1/labels", response_model=LabelRead, status_code=201, tags=["labels"])
def create_label(payload: LabelCreate, db: Session = Depends(get_db)) -> Label:
    get_user(db, payload.owner_id)
    label = Label(**payload.model_dump())
    db.add(label)
    commit(db, "That owner already has a label with this name.")
    db.refresh(label)
    return label


@app.get("/api/v1/labels", response_model=list[LabelRead], tags=["labels"])
def list_labels(
    owner_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[Label]:
    query = select(Label).order_by(Label.name, Label.id)
    if owner_id:
        query = query.where(Label.owner_id == owner_id)
    return list(db.scalars(query))


@app.patch("/api/v1/labels/{label_id}", response_model=LabelRead, tags=["labels"])
def update_label(
    label_id: UUID, payload: LabelUpdate, db: Session = Depends(get_db)
) -> Label:
    label = db.get(Label, label_id)
    if not label:
        raise not_found("Label", label_id)
    changes = payload.model_dump(exclude_unset=True)
    if any(changes.get(field, "valid") is None for field in ("name", "color")):
        raise ProblemError(422, "Invalid label", "Label fields cannot be null.", "validation")
    for field, value in changes.items():
        setattr(label, field, value)
    commit(db, "That owner already has a label with this name.")
    db.refresh(label)
    return label


@app.delete("/api/v1/labels/{label_id}", status_code=204, tags=["labels"])
def delete_label(label_id: UUID, db: Session = Depends(get_db)) -> Response:
    label = db.get(Label, label_id)
    if not label:
        raise not_found("Label", label_id)
    db.delete(label)
    db.commit()
    return Response(status_code=204)


@app.post("/api/v1/tasks", response_model=TaskRead, status_code=201, tags=["tasks"])
def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
    project = get_project(db, payload.project_id)
    labels = labels_for_owner(db, payload.label_ids, project.owner_id)
    values = payload.model_dump(exclude={"label_ids"})
    values["status"] = payload.status.value
    task = Task(**values, labels=labels)
    db.add(task)
    db.commit()
    db.refresh(task)
    return get_task(db, task.id)


@app.get("/api/v1/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def read_task(task_id: UUID, db: Session = Depends(get_db)) -> Task:
    return get_task(db, task_id)


@app.get("/api/v1/tasks", response_model=TaskPage, tags=["tasks"])
def list_tasks(
    project_id: UUID | None = None,
    status: str | None = Query(None, pattern="^(todo|in_progress|done)$"),
    label_id: UUID | None = None,
    due_before: datetime | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int | None = Query(None, ge=0),
    cursor: str | None = None,
    db: Session = Depends(get_db),
) -> TaskPage:
    if cursor and offset is not None:
        raise ProblemError(
            400,
            "Choose one pagination mode",
            "Cursor and offset cannot be used together.",
            "pagination-conflict",
        )

    filters = []
    if project_id:
        filters.append(Task.project_id == project_id)
    if status:
        filters.append(Task.status == status)
    if label_id:
        filters.append(Task.labels.any(Label.id == label_id))
    if due_before:
        filters.append(Task.due_at <= due_before)

    query = (
        select(Task)
        .where(*filters)
        .options(selectinload(Task.labels))
        .order_by(Task.created_at.desc(), Task.id.desc())
    )
    if cursor:
        cursor_time, cursor_id = decode_cursor(cursor)
        query = query.where(
            or_(
                Task.created_at < cursor_time,
                and_(Task.created_at == cursor_time, Task.id < cursor_id),
            )
        )
    elif offset is not None:
        query = query.offset(offset)

    items = list(db.scalars(query.limit(limit + 1)).unique())
    has_more = len(items) > limit
    items = items[:limit]
    total = db.scalar(select(func.count()).select_from(Task).where(*filters)) or 0
    next_cursor = encode_cursor(items[-1]) if has_more and items else None
    return TaskPage(items=items, total=total, next_cursor=next_cursor)


@app.patch("/api/v1/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def update_task(
    task_id: UUID, payload: TaskUpdate, db: Session = Depends(get_db)
) -> Task:
    current = get_task(db, task_id)
    changes = payload.model_dump(exclude_unset=True, exclude={"version", "label_ids"})
    if any(changes.get(field, "valid") is None for field in ("title", "status")):
        raise ProblemError(422, "Invalid task", "Title and status cannot be null.", "validation")
    if payload.status is not None:
        changes["status"] = payload.status.value
    changes["version"] = Task.version + 1
    changes["updated_at"] = func.now()

    updated_id = db.scalar(
        update(Task)
        .where(Task.id == task_id, Task.version == payload.version)
        .values(**changes)
        .returning(Task.id)
    )
    if not updated_id:
        db.rollback()
        if db.get(Task, task_id):
            raise ProblemError(
                409,
                "Task version conflict",
                f"Expected version {payload.version}; reload the task and retry.",
                "version-conflict",
            )
        raise not_found("Task", task_id)

    if payload.label_ids is not None:
        project = get_project(db, current.project_id)
        current.labels = labels_for_owner(db, payload.label_ids, project.owner_id)
    db.commit()
    return get_task(db, task_id)


@app.delete("/api/v1/tasks/{task_id}", status_code=204, tags=["tasks"])
def delete_task(
    task_id: UUID,
    version: int = Query(..., ge=1),
    db: Session = Depends(get_db),
) -> Response:
    deleted_id = db.scalar(
        delete(Task)
        .where(Task.id == task_id, Task.version == version)
        .returning(Task.id)
    )
    if not deleted_id:
        db.rollback()
        if db.get(Task, task_id):
            raise ProblemError(
                409,
                "Task version conflict",
                f"Expected version {version}; reload the task and retry.",
                "version-conflict",
            )
        raise not_found("Task", task_id)
    db.commit()
    return Response(status_code=204)
