"""Модель задачи для менеджера задач."""

import uuid
from enum import Enum
from sqlalchemy import Column, String, Text, Enum as SQLEnum
from app.database import Base


class TaskStatus(str, Enum):
    """Статусы задач."""

    CREATED = "создано"
    IN_PROGRESS = "в работе"
    COMPLETED = "завершено"


class Task(Base):
    """Модель задачи.

    Атрибуты:
        id: Уникальный идентификатор задачи (UUID)
        title: Название задачи
        description: Описание задачи
        status: Статус задачи (создано, в работе, завершено)
    """

    __tablename__ = "tasks"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TaskStatus),
        default=TaskStatus.CREATED,
        nullable=False
    )

    def __repr__(self):
        """Строковое представление задачи."""
        return (
            f"<Task(id={self.id}, title='{self.title}', "
            f"status='{self.status}')>"
        )
