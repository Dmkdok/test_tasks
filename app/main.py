"""Главное приложение менеджера задач."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.models import task
from app.api import tasks

# Создание таблиц в базе данных
task.Base.metadata.create_all(bind=engine)

# Создание приложения FastAPI
app = FastAPI(
    title="Менеджер задач",
    description="API для управления задачами с CRUD операциями",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(tasks.router)


@app.get("/")
def read_root():
    """Корневой endpoint для проверки работоспособности API."""
    return {
        "message": "Добро пожаловать в Менеджер задач!",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Проверка состояния приложения."""
    return {"status": "healthy"}
