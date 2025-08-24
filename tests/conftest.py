"""Конфигурация pytest для тестирования менеджера задач."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.task import TaskStatus


# Создание тестовой базы данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    """Переопределение функции получения базы данных для тестов."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для создания сессии базы данных для каждого теста."""
    # Создание таблиц
    Base.metadata.create_all(bind=engine)

    # Создание сессии
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Очистка таблиц после каждого теста
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для создания тестового клиента."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_task_data():
    """Фикстура с примером данных задачи."""
    return {
        "title": "Тестовая задача",
        "description": "Описание тестовой задачи",
        "status": TaskStatus.CREATED
    }


@pytest.fixture
def sample_task_update_data():
    """Фикстура с примером данных для обновления задачи."""
    return {
        "title": "Обновленная задача",
        "status": TaskStatus.IN_PROGRESS
    }
