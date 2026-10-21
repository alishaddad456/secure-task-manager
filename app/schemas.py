
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Title must not be blank")

        return value


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Title must not be blank")

        return value


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime
