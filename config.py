import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Загрузка .env файла
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Конфигурация базы данных
    DATABASE_URL: str = os.getenv("POSTGRES_DATABASE_URL_2")

    # Конфигурация MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "chokofinder")
    MONGODB_COLLECTION_NAME: str = os.getenv("MONGODB_COLLECTION_NAME", "documents")

    # Конфигурация JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  

    # Конфигурация приложения
    DOCS_DIRECTORY: str = os.getenv("DOCS_DIRECTORY", "Docs")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    DEFAULT_ADMIN_USERNAME: str = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_EMAIL: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    DEFAULT_ADMIN_PASSWORD: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    CHUNK_SIZE: int = os.getenv("CHUNK_SIZE", "512")
    CHUNK_OVERLAP: int = os.getenv("CHUNK_OVERLAP", "50")

    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "DATABASE\\")
    USE_MONGODB: bool = os.getenv("USE_MONGODB", "True").lower() == "true"

    # OpenAI configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

    class Config:
        case_sensitive = True


settings = Settings()