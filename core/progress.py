from typing import Dict, Optional
from threading import Lock

# Глобальный объект для хранения статуса прогресса
progress_data = {
    "is_processing": False,
    "total_files": 0,
    "processed_files": 0,
    "total_documents": 0,
    "processed_documents": 0,
    "current_stage": "",
    "percent_complete": 0,
    "error": None
}


progress_lock = Lock()

def get_progress() -> Dict:
    """Получить текущий статус прогресса"""
    with progress_lock:
        return progress_data.copy()

def update_progress(
    is_processing: Optional[bool] = None,
    total_files: Optional[int] = None,
    processed_files: Optional[int] = None,
    total_documents: Optional[int] = None,
    processed_documents: Optional[int] = None,
    current_stage: Optional[str] = None,
    error: Optional[str] = None,
    percent_complete: Optional[int] = None
) -> None:
    """Обновить статус прогресса"""
    with progress_lock:
        if is_processing is not None:
            progress_data["is_processing"] = is_processing
        
        if total_files is not None:
            progress_data["total_files"] = total_files
        
        if processed_files is not None:
            progress_data["processed_files"] = processed_files
            if progress_data["total_files"] > 0 and percent_complete is None:
                # 50% прогресса на обработку файлов
                file_percent = (processed_files / progress_data["total_files"]) * 50
                progress_data["percent_complete"] = int(file_percent)
        
        if total_documents is not None:
            progress_data["total_documents"] = total_documents
        
        if processed_documents is not None:
            progress_data["processed_documents"] = processed_documents
            if progress_data["total_documents"] > 0 and percent_complete is None:
                # 50% прогресса на создание эмбеддингов и загрузку в базу
                doc_percent = (processed_documents / progress_data["total_documents"]) * 50
                progress_data["percent_complete"] = int(50 + doc_percent)
        
        if current_stage is not None:
            progress_data["current_stage"] = current_stage
        
        if percent_complete is not None:
            progress_data["percent_complete"] = percent_complete
        
        if error is not None:
            progress_data["error"] = error
            progress_data["is_processing"] = False 