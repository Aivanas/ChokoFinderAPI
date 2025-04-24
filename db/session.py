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
    try:
        engine = create_engine(
            settings.DATABASE_URL,
        )
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Успешное подключение к базе данных")
        return engine
    except OperationalError as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        if settings.DEBUG:
            logger.warning("Используется SQLite как запасной вариант")
            return create_engine("sqlite:///./fallback.db")
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