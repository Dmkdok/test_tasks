"""Тесты для API задач."""
from app.models.task import TaskStatus
from app.crud.task import TaskCRUD
from app.schemas.task import TaskCreate, TaskUpdate


class TestTaskCRUD:
    """Тесты для CRUD операций с задачами."""

    def test_create_task(self, db_session, sample_task_data):
        """Тест создания задачи."""
        task_create = TaskCreate(**sample_task_data)
        task = TaskCRUD.create_task(db_session, task_create)

        assert task.title == sample_task_data["title"]
        assert task.description == sample_task_data["description"]
        assert task.status == sample_task_data["status"]
        assert task.id is not None

    def test_get_task(self, db_session, sample_task_data):
        """Тест получения задачи по ID."""
        # Создаем задачу
        task_create = TaskCreate(**sample_task_data)
        created_task = TaskCRUD.create_task(db_session, task_create)

        # Получаем задачу
        task = TaskCRUD.get_task(db_session, created_task.id)

        assert task is not None
        assert task.id == created_task.id
        assert task.title == sample_task_data["title"]

    def test_get_task_not_found(self, db_session):
        """Тест получения несуществующей задачи."""
        task = TaskCRUD.get_task(db_session, "non-existent-id")
        assert task is None

    def test_get_tasks(self, db_session, sample_task_data):
        """Тест получения списка задач."""
        # Создаем несколько задач
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data["title"] = f"Задача {i}"
            task_create = TaskCreate(**task_data)
            TaskCRUD.create_task(db_session, task_create)

        # Получаем список задач
        tasks = TaskCRUD.get_tasks(db_session)

        assert len(tasks) == 3
        assert all(task.title.startswith("Задача") for task in tasks)

    def test_get_tasks_with_filter(self, db_session, sample_task_data):
        """Тест получения списка задач с фильтром по статусу."""
        # Создаем задачи с разными статусами
        statuses = [
            TaskStatus.CREATED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED
        ]
        for status in statuses:
            task_data = sample_task_data.copy()
            task_data["status"] = status
            task_create = TaskCreate(**task_data)
            TaskCRUD.create_task(db_session, task_create)

        # Получаем задачи с фильтром
        tasks = TaskCRUD.get_tasks(db_session, status=TaskStatus.CREATED)

        assert len(tasks) == 1
        assert tasks[0].status == TaskStatus.CREATED

    def test_update_task(
        self,
        db_session,
        sample_task_data,
        sample_task_update_data
    ):
        """Тест обновления задачи."""
        # Создаем задачу
        task_create = TaskCreate(**sample_task_data)
        created_task = TaskCRUD.create_task(db_session, task_create)

        # Обновляем задачу
        task_update = TaskUpdate(**sample_task_update_data)
        updated_task = TaskCRUD.update_task(
            db_session,
            created_task.id,
            task_update
        )

        assert updated_task is not None
        assert updated_task.title == sample_task_update_data["title"]
        assert updated_task.status == sample_task_update_data["status"]
        # Не изменилось
        assert updated_task.description == sample_task_data["description"]

    def test_update_task_not_found(
        self,
        db_session,
        sample_task_update_data
    ):
        """Тест обновления несуществующей задачи."""
        task_update = TaskUpdate(**sample_task_update_data)
        result = TaskCRUD.update_task(
            db_session,
            "non-existent-id",
            task_update
        )

        assert result is None

    def test_delete_task(self, db_session, sample_task_data):
        """Тест удаления задачи."""
        # Создаем задачу
        task_create = TaskCreate(**sample_task_data)
        created_task = TaskCRUD.create_task(db_session, task_create)

        # Удаляем задачу
        success = TaskCRUD.delete_task(db_session, created_task.id)

        assert success is True

        # Проверяем, что задача удалена
        task = TaskCRUD.get_task(db_session, created_task.id)
        assert task is None

    def test_delete_task_not_found(self, db_session):
        """Тест удаления несуществующей задачи."""
        success = TaskCRUD.delete_task(db_session, "non-existent-id")
        assert success is False


class TestTaskAPI:
    """Тесты для API endpoints."""

    def test_create_task_api(self, client, sample_task_data):
        """Тест API создания задачи."""
        response = client.post("/tasks/", json=sample_task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["status"] == sample_task_data["status"]
        assert "id" in data

    def test_create_task_invalid_data(self, client):
        """Тест API создания задачи с невалидными данными."""
        invalid_data = {"title": ""}  # Пустое название
        response = client.post("/tasks/", json=invalid_data)

        assert response.status_code == 422

    def test_get_task_api(self, client, sample_task_data):
        """Тест API получения задачи."""
        # Создаем задачу
        create_response = client.post("/tasks/", json=sample_task_data)
        task_id = create_response.json()["id"]

        # Получаем задачу
        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task_data["title"]

    def test_get_task_not_found_api(self, client):
        """Тест API получения несуществующей задачи."""
        response = client.get("/tasks/non-existent-id")

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]

    def test_get_tasks_api(self, client, sample_task_data):
        """Тест API получения списка задач."""
        # Создаем несколько задач
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data["title"] = f"Задача {i}"
            client.post("/tasks/", json=task_data)

        # Получаем список задач
        response = client.get("/tasks/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_tasks_with_pagination(self, client, sample_task_data):
        """Тест API получения списка задач с пагинацией."""
        # Создаем несколько задач
        for i in range(5):
            task_data = sample_task_data.copy()
            task_data["title"] = f"Задача {i}"
            client.post("/tasks/", json=task_data)

        # Получаем задачи с пагинацией
        response = client.get("/tasks/?skip=2&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_tasks_with_status_filter(self, client, sample_task_data):
        """Тест API получения списка задач с фильтром по статусу."""
        # Создаем задачи с разными статусами
        statuses = ["создано", "в работе", "завершено"]
        for status in statuses:
            task_data = sample_task_data.copy()
            task_data["status"] = status
            client.post("/tasks/", json=task_data)

        # Получаем задачи с фильтром
        response = client.get("/tasks/?status=создано")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "создано"

    def test_update_task_api(
        self,
        client,
        sample_task_data,
        sample_task_update_data
    ):
        """Тест API обновления задачи."""
        # Создаем задачу
        create_response = client.post("/tasks/", json=sample_task_data)
        task_id = create_response.json()["id"]

        # Обновляем задачу
        response = client.put(
            f"/tasks/{task_id}",
            json=sample_task_update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_task_update_data["title"]
        assert data["status"] == sample_task_update_data["status"]

    def test_update_task_not_found_api(
        self,
        client,
        sample_task_update_data
    ):
        """Тест API обновления несуществующей задачи."""
        response = client.put(
            "/tasks/non-existent-id",
            json=sample_task_update_data
        )

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]

    def test_delete_task_api(self, client, sample_task_data):
        """Тест API удаления задачи."""
        # Создаем задачу
        create_response = client.post("/tasks/", json=sample_task_data)
        task_id = create_response.json()["id"]

        # Удаляем задачу
        response = client.delete(f"/tasks/{task_id}")

        assert response.status_code == 204

        # Проверяем, что задача удалена
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found_api(self, client):
        """Тест API удаления несуществующей задачи."""
        response = client.delete("/tasks/non-existent-id")

        assert response.status_code == 404
        assert "не найдена" in response.json()["detail"]


class TestTaskValidation:
    """Тесты валидации данных."""

    def test_task_title_validation(self, client):
        """Тест валидации названия задачи."""
        # Пустое название
        response = client.post("/tasks/", json={"title": ""})
        assert response.status_code == 422

        # Слишком длинное название
        long_title = "a" * 256
        response = client.post("/tasks/", json={"title": long_title})
        assert response.status_code == 422

    def test_task_status_validation(self, client):
        """Тест валидации статуса задачи."""
        # Невалидный статус
        response = client.post("/tasks/", json={
            "title": "Тест",
            "status": "невалидный_статус"
        })
        assert response.status_code == 422

    def test_pagination_validation(self, client):
        """Тест валидации параметров пагинации."""
        # Отрицательный skip
        response = client.get("/tasks/?skip=-1")
        assert response.status_code == 422

        # Нулевой limit
        response = client.get("/tasks/?limit=0")
        assert response.status_code == 422

        # Слишком большой limit
        response = client.get("/tasks/?limit=1001")
        assert response.status_code == 422
