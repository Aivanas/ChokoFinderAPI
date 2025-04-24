
WORDS_FRAGMENTATION_COUNT = 200
CHUNK_SIZE = 1000

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загрузка .env файла
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Конфигурация базы данных
    DATABASE_URL: str = os.getenv("POSTGRES_DATABASE_URL")

    # Конфигурация JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Конфигурация приложения
    DOCS_DIRECTORY: str = os.getenv("DOCS_DIRECTORY", "Docs")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    class Config:
        case_sensitive = True


settings = Settings()