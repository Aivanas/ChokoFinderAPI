import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_engine():
    """Создает и возвращает движок SQLAlchemy"""
    logger.info(f"Попытка подключения к базе данных с URL: {settings.DATABASE_URL}")
    try:
        engine = create_engine(
            settings.DATABASE_URL,
        )
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database(), current_user, version()"))
            row = result.fetchone()
            logger.info(f"Подключение успешно. База данных: {row[0]}, пользователь: {row[1]}, версия: {row[2]}")
        return engine
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных типа {type(e).__name__}: {str(e)}")
        raise

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Зависимость для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()