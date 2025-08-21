"""CRUD операции для задач."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


class TaskCRUD:
    """Класс для CRUD операций с задачами."""

    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        """Создание новой задачи.

        Args:
            db: Сессия базы данных
            task: Данные для создания задачи

        Returns:
            Созданная задача
        """
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_task(db: Session, task_id: str) -> Optional[Task]:
        """Получение задачи по ID.

        Args:
            db: Сессия базы данных
            task_id: ID задачи

        Returns:
            Задача или None если не найдена
        """
        return db.query(Task).filter(Task.id == task_id).first()

    @staticmethod
    def get_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Task]:
        """Получение списка задач с пагинацией и фильтрацией.

        Args:
            db: Сессия базы данных
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            status: Фильтр по статусу

        Returns:
            Список задач
        """
        query = db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_task(
        db: Session,
        task_id: str,
        task_update: TaskUpdate
    ) -> Optional[Task]:
        """Обновление задачи.

        Args:
            db: Сессия базы данных
            task_id: ID задачи
            task_update: Данные для обновления

        Returns:
            Обновленная задача или None если не найдена
        """
        db_task = TaskCRUD.get_task(db, task_id)
        if not db_task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        db.commit()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def delete_task(db: Session, task_id: str) -> bool:
        """Удаление задачи.

        Args:
            db: Сессия базы данных
            task_id: ID задачи

        Returns:
            True если задача удалена, False если не найдена
        """
        db_task = TaskCRUD.get_task(db, task_id)
        if not db_task:
            return False

        db.delete(db_task)
        db.commit()
        return True
