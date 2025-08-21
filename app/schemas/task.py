"""Pydantic схемы для задач."""

from typing import Optional
from pydantic import BaseModel, Field
from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """Базовая схема задачи."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Название задачи"
    )
    description: Optional[str] = Field(
        None,
        description="Описание задачи"
    )
    status: TaskStatus = Field(
        TaskStatus.CREATED,
        description="Статус задачи"
    )


class TaskCreate(TaskBase):
    """Схема для создания задачи."""

    pass


class TaskUpdate(BaseModel):
    """Схема для обновления задачи."""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Название задачи"
    )
    description: Optional[str] = Field(
        None,
        description="Описание задачи"
    )
    status: Optional[TaskStatus] = Field(
        None,
        description="Статус задачи"
    )


class TaskResponse(TaskBase):
    """Схема для ответа с задачей."""

    id: str = Field(
        ...,
        description="Уникальный идентификатор задачи"
    )

    model_config = {"from_attributes": True}
