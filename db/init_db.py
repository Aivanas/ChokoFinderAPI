import logging
from sqlalchemy.orm import Session
from core.security import get_password_hash
from models.user import User
from config import settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные администратора по умолчанию (можно переместить в .env)
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = "admin123"  # Лучше брать из .env или генерировать случайный пароль


def init_db(db: Session) -> None:
    """Инициализация базы данных с созданием администратора по умолчанию"""
    # Проверка наличия администратора
    user = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()

    if not user:
        logger.info("Создание администратора по умолчанию")

        # Получение настроек из .env, если они там есть
        admin_username = getattr(settings, "DEFAULT_ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
        admin_email = getattr(settings, "DEFAULT_ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL)
        admin_password = getattr(settings, "DEFAULT_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)

        admin = User(
            username=admin_username,
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            is_admin=True,
            is_active=True
        )

        db.add(admin)
        db.commit()

        logger.info(f"Администратор создан: username={admin_username}, email={admin_email}")
        if DEFAULT_ADMIN_PASSWORD == admin_password:
            logger.warning(
                "Используется пароль администратора по умолчанию. Рекомендуется сменить его из соображений безопасности.")
    else:
        logger.info("Администратор уже существует, пропускаем создание.")