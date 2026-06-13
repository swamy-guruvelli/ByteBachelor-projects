from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import TaskStatus


class ReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=80)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=80)


class UserRead(ReadModel):
    id: UUID
    email: EmailStr
    display_name: str
    created_at: datetime


class ProjectCreate(BaseModel):
    owner_id: UUID
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2_000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2_000)


class ProjectRead(ReadModel):
    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class LabelCreate(BaseModel):
    owner_id: UUID
    name: str = Field(min_length=1, max_length=40)
    color: str = "#64748b"

    @field_validator("color")
    @classmethod
    def valid_hex_color(cls, value: str) -> str:
        if len(value) != 7 or not value.startswith("#"):
            raise ValueError("color must use #RRGGBB format")
        try:
            int(value[1:], 16)
        except ValueError as error:
            raise ValueError("color must use #RRGGBB format") from error
        return value.lower()


class LabelRead(ReadModel):
    id: UUID
    owner_id: UUID
    name: str
    color: str
    created_at: datetime


class LabelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=40)
    color: str | None = None

    @field_validator("color")
    @classmethod
    def valid_optional_hex_color(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return LabelCreate.valid_hex_color(value)


class TaskCreate(BaseModel):
    project_id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10_000)
    status: TaskStatus = TaskStatus.TODO
    due_at: AwareDatetime | None = None
    label_ids: list[UUID] = Field(default_factory=list, max_length=20)


class TaskUpdate(BaseModel):
    version: int = Field(ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10_000)
    status: TaskStatus | None = None
    due_at: AwareDatetime | None = None
    label_ids: list[UUID] | None = Field(default=None, max_length=20)


class TaskRead(ReadModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    due_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime
    labels: list[LabelRead]


class TaskPage(BaseModel):
    items: list[TaskRead]
    total: int
    next_cursor: str | None


class Problem(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    errors: list[dict] | None = None
