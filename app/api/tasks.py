"""API endpoints для задач."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.task import TaskCRUD
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.models.task import TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Создание новой задачи.

    - **title**: Название задачи (обязательно)
    - **description**: Описание задачи (опционально)
    - **status**: Статус задачи (по умолчанию "создано")
    """
    return TaskCRUD.create_task(db=db, task=task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Получение задачи по ID.

    - **task_id**: Уникальный идентификатор задачи
    """
    task = TaskCRUD.get_task(db=db, task_id=task_id)
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
    return task


@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = Query(
        0,
        ge=0,
        description="Количество записей для пропуска"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Максимальное количество записей"
    ),
    status: Optional[TaskStatus] = Query(
        None,
        description="Фильтр по статусу"
    ),
    db: Session = Depends(get_db)
) -> List[TaskResponse]:
    """Получение списка задач с пагинацией и фильтрацией.

    - **skip**: Количество записей для пропуска (по умолчанию 0)
    - **limit**: Максимальное количество записей
      (по умолчанию 100, максимум 1000)
    - **status**: Фильтр по статусу (опционально)
    """
    return TaskCRUD.get_tasks(
        db=db,
        skip=skip,
        limit=limit,
        status=status
    )


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Обновление задачи.

    - **task_id**: Уникальный идентификатор задачи
    - **title**: Новое название задачи (опционально)
    - **description**: Новое описание задачи (опционально)
    - **status**: Новый статус задачи (опционально)
    """
    task = TaskCRUD.update_task(
        db=db,
        task_id=task_id,
        task_update=task_update
    )
    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
) -> None:
    """Удаление задачи.

    - **task_id**: Уникальный идентификатор задачи
    """
    success = TaskCRUD.delete_task(db=db, task_id=task_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Задача не найдена"
        )
