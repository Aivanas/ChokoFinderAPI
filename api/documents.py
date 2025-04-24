import os
import aiofiles
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session

from config import settings
from core.deps import get_current_admin_user, get_current_active_user
from db.session import get_db
from models.user import User

# Импорт функции обработки векторной базы
# Предполагается, что она у вас уже реализована
from services.FilesHandler import process_files_to_vector_db

router = APIRouter()


@router.get("/update-base", status_code=200)
async def update_vector_base(
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_admin_user)
):
    """Обновление векторной базы (только для администраторов)"""
    background_tasks.add_task(process_files_to_vector_db)
    return {"message": "Обработка запущена"}


@router.post("/upload", status_code=200)
async def upload_files(
        files: List[UploadFile],
        current_user: User = Depends(get_current_admin_user)
):
    """Загрузка документов (только для администраторов)"""
    # Создаем директорию, если не существует
    os.makedirs(settings.DOCS_DIRECTORY, exist_ok=True)

    uploaded_files = []
    for file in files:
        file_path = os.path.join(settings.DOCS_DIRECTORY, file.filename)
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        uploaded_files.append(file.filename)

    return {"filename": uploaded_files, "result": "OK"}


@router.delete("/{filename}", status_code=200)
async def delete_document(
        filename: str,
        current_user: User = Depends(get_current_admin_user)
):
    """Удаление документа (только для администраторов)"""
    file_path = os.path.join(settings.DOCS_DIRECTORY, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    os.remove(file_path)
    return {"message": f"File {filename} deleted successfully"}


@router.get("/", response_model=List[str])
async def list_documents(
        current_user: User = Depends(get_current_active_user)
):
    """Получение списка документов (для всех пользователей)"""
    if not os.path.exists(settings.DOCS_DIRECTORY):
        return []

    files = os.listdir(settings.DOCS_DIRECTORY)
    return files