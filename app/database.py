"""Конфигурация базы данных для менеджера задач."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL базы данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# Создание движка базы данных
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Генератор для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
