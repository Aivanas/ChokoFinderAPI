from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.deps import get_current_admin_user, get_current_active_user
from core.security import get_password_hash
from db.session import get_db
from models.user import User
from schemas.user import UserInDB, UserUpdate
from config import settings

router = APIRouter()


@router.get("/me", response_model=UserInDB)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@router.get("/", response_model=List[UserInDB])
async def read_users(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Получение списка пользователей (только для администраторов)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Обновление информации о пользователе (только для администраторов)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Удаление пользователя (только для администраторов)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return None


@router.post("/admin/reset-password", response_model=UserInDB)
async def reset_admin_password(
        current_user: User = Depends(get_current_admin_user),
        db: Session = Depends(get_db)
):
    """Сброс пароля администратора на пароль по умолчанию (только для администраторов)"""
    admin = db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USERNAME).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin user not found")

    admin.hashed_password = get_password_hash(settings.DEFAULT_ADMIN_PASSWORD)
    db.commit()
    db.refresh(admin)

    return admin