import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from api import api_router
from config import settings
from core.metrics import MetricsMiddleware
from db.base import Base
from db.session import engine, SessionLocal
from db.init_db import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title="RAG Agent API",
    description="API для работы с RAG агентом",
    version="0.1.0",
    debug=settings.DEBUG
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Инициализация базы данных
def setup_db():
    try:
        # Создание таблиц
        Base.metadata.create_all(bind=engine)
        logger.info("Таблицы в базе данных успешно созданы")

        # Инициализация начальных данных
        db = SessionLocal()
        try:
            init_db(db)
        finally:
            db.close()

    except OperationalError as e:
        logger.error(f"Не удалось инициализировать базу данных: {e}")
        if settings.DEBUG:
            logger.warning("Режим отладки: продолжаем работу")
        else:
            logger.error("Критическая ошибка: приложение не может запуститься без базы данных")
            import sys
            sys.exit(1)



setup_db()

app.include_router(api_router)
app.add_middleware(MetricsMiddleware)

os.makedirs(settings.DOCS_DIRECTORY, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to RAG Agent API"}

@app.get("/health")
async def health_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


if __name__ == "__main__":
    import uvicorn
    from prometheus_client import start_http_server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    start_http_server(8010)