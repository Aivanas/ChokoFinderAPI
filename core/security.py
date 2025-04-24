import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from config import settings


def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    # bcrypt требует байтовые строки для сравнения
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_password, hashed_password)


def get_password_hash(password):
    """Хеширование пароля"""
    # Преобразуем пароль в байты, если он передан как строка
    if isinstance(password, str):
        password = password.encode('utf-8')

    # Генерируем соль и хешируем пароль
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    # Возвращаем хеш в виде строки
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt