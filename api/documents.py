import os
import aiofiles
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session

from config import settings
from core.deps import get_current_admin_user, get_current_active_user
from db.session import get_db
from models.user import User

# Импорт функции обработки векторной базы
# Предполагается, что она у вас уже реализована
from services.FilesHandler import process_files_to_vector_db, delete_from_vector_db
from services.mongodb_handler import (
    save_file_to_mongodb, 
    get_file_from_mongodb, 
    delete_file_from_mongodb, 
    list_files_from_mongodb
)
from core.metrics import UPDATE_BASE_COUNT, UPLOADED_FILES_COUNT, FILE_SIZE_HISTOGRAM, DELETED_FILES_COUNT, \
    DOCUMENTS_COUNT
from core.progress import get_progress

router = APIRouter()

# Список разрешенных форматов документов
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.txt', '.docx', '.doc', '.rtf', '.md', '.markdown', 
    '.odt', '.tex', '.html', '.htm'
}


@router.get("/update-base", status_code=200)
async def update_vector_base(
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_admin_user)
):
    """Обновление векторной базы (только для администраторов)"""
    background_tasks.add_task(process_files_to_vector_db)
    UPDATE_BASE_COUNT.inc()
    return {"message": "Обработка запущена"}


@router.get("/update-progress", response_model=Dict, status_code=200)
async def get_update_progress(
    current_user: User = Depends(get_current_active_user)
):
    """Получение статуса прогресса обновления векторной базы (для всех активных пользователей)"""
    return get_progress()


@router.post("/upload", status_code=200)
async def upload_files(
        files: List[UploadFile],
        current_user: User = Depends(get_current_admin_user)
):
    """Загрузка документов (только для администраторов)"""
    # Create docs directory for temp files if it doesn't exist
    os.makedirs(settings.DOCS_DIRECTORY, exist_ok=True)

    uploaded_files = []
    for file in files:
        try:
            # Check file extension
            _, file_ext = os.path.splitext(file.filename.lower())
            if file_ext not in ALLOWED_DOCUMENT_EXTENSIONS:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Неподдерживаемый формат файла: {file_ext}. Разрешены только: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}"
                )
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            FILE_SIZE_HISTOGRAM.observe(file_size)
            
            if settings.USE_MONGODB:
                # Save file to MongoDB
                filename = await save_file_to_mongodb(file.filename, content)
                uploaded_files.append(filename)
            else:
                # Save file to local filesystem (legacy method)
                file_path = os.path.join(settings.DOCS_DIRECTORY, file.filename)
                async with aiofiles.open(file_path, "wb") as out_file:
                    await out_file.write(content)
                uploaded_files.append(file.filename)
            
            UPLOADED_FILES_COUNT.inc()
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading file {file.filename}: {str(e)}")

    return {"filename": uploaded_files, "result": "OK"}


@router.delete("/{filename}", status_code=200)
async def delete_document(
        filename: str,
        current_user: User = Depends(get_current_admin_user)
):
    """Удаление документа (только для администраторов)"""
    if settings.USE_MONGODB:
        # Delete from MongoDB
        success = await delete_file_from_mongodb(filename)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
    else:
        # Delete from local filesystem (legacy method)
        file_path = os.path.join(settings.DOCS_DIRECTORY, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        os.remove(file_path)
    
    # Delete from vector database
    await delete_from_vector_db(filename)
        
    DELETED_FILES_COUNT.inc()
    return {"message": f"File {filename} deleted successfully"}


@router.get("/", response_model=List[str])
async def list_documents(
        current_user: User = Depends(get_current_admin_user)
):
    """Получение списка документов (для всех пользователей)"""
    if settings.USE_MONGODB:
        # Get files from MongoDB
        files = await list_files_from_mongodb()
    else:
        # Get files from local filesystem (legacy method)
        if not os.path.exists(settings.DOCS_DIRECTORY):
            files = []
        else:
            files = os.listdir(settings.DOCS_DIRECTORY)
            
    DOCUMENTS_COUNT.set(len(files))
    return files