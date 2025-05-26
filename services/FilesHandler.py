import os
import getpass
from glob import glob
import asyncio
import pathlib

from dotenv import load_dotenv, find_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredRTFLoader,
    UnstructuredODTLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.config import Settings
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
from langchain_gigachat.chat_models import GigaChat
from config import settings
from core.progress import update_progress
from services.mongodb_handler import get_file_from_mongodb, list_files_from_mongodb, get_temp_file_path

# Store the vector database in MongoDB or local directory based on settings
db_path = "DATABASE\\" if not settings.USE_MONGODB else None

# Список разрешенных форматов документов (должен совпадать с api/documents.py)
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.txt', '.docx', '.doc', '.rtf', '.md', '.markdown', 
    '.odt', '.tex', '.html', '.htm'
}

# Map file extensions to appropriate document loaders
DOCUMENT_LOADERS = {
    '.pdf': PyPDFLoader,
    '.txt': TextLoader,
    '.docx': Docx2txtLoader,
    '.doc': Docx2txtLoader,  # Note: Requires antiword for .doc files
    '.rtf': UnstructuredRTFLoader,
    '.md': UnstructuredMarkdownLoader,
    '.markdown': UnstructuredMarkdownLoader,
    '.odt': UnstructuredODTLoader,
    '.html': UnstructuredHTMLLoader,
    '.htm': UnstructuredHTMLLoader,
    '.tex': TextLoader,
}

async def delete_from_vector_db(filename: str) -> bool:
    """Delete document from vector database by its filename"""
    try:
        embeddings = OpenAIEmbeddings()
        
        # Setup Chroma DB with appropriate configuration
        if settings.USE_MONGODB:
            db = Chroma(
                collection_name="RAG",
                embedding_function=embeddings,
                client_settings=Settings(anonymized_telemetry=False),
                # When using MongoDB with Chroma, we don't specify persist_directory
            )
        else:
            db = Chroma(
                collection_name="RAG",
                embedding_function=embeddings,
                client_settings=Settings(anonymized_telemetry=False),
                persist_directory=db_path
            )
        
        # Get all documents from the collection
        result = db.get()
        
        # Find documents with source path containing the filename
        # Chroma stores document sources in the metadata
        ids_to_delete = []
        if result and result.get('metadatas'):
            for i, metadata in enumerate(result['metadatas']):
                if metadata and 'source' in metadata:
                    # Check if the source path contains our filename
                    source = metadata['source']
                    if os.path.basename(source) == filename or filename in source:
                        ids_to_delete.append(result['ids'][i])
        
        # Delete the matching documents
        if ids_to_delete:
            db._collection.delete(ids=ids_to_delete)
            print(f"Deleted {len(ids_to_delete)} document chunks from vector database for file {filename}")
            return True
        else:
            print(f"No documents found in vector database for file {filename}")
            return False
            
    except Exception as e:
        print(f"Error deleting from vector DB: {str(e)}")
        return False

async def process_files_to_vector_db():
    try:
        # Устанавливаем начальный статус
        update_progress(
            is_processing=True,
            current_stage="Поиск документов",
            processed_files=0,
            processed_documents=0,
            percent_complete=0
        )
        
        # If using MongoDB, get files from there, otherwise use filesystem
        if settings.USE_MONGODB:
            # Get list of files from MongoDB
            files_list = await list_files_from_mongodb()
            # Filter by allowed extensions
            doc_files = [f for f in files_list if pathlib.Path(f).suffix.lower() in ALLOWED_DOCUMENT_EXTENSIONS]
            update_progress(total_files=len(doc_files), current_stage="Загрузка документов из MongoDB")
        else:
            directory = "Docs\\"
            doc_files = []
            for ext in ALLOWED_DOCUMENT_EXTENSIONS:
                doc_files.extend(glob(os.path.join(directory, f"*{ext}")))
            update_progress(total_files=len(doc_files), current_stage="Загрузка документов из локальной папки")
        
        documents = []
        processed_files = 0
        
        for filename in doc_files:
            try:
                # Get file extension to determine the loader
                file_ext = pathlib.Path(filename).suffix.lower()
                
                # Skip if extension not supported by loaders
                if file_ext not in DOCUMENT_LOADERS:
                    update_progress(current_stage=f"Формат файла {file_ext} не поддерживается")
                    continue
                
                # Get the appropriate loader class
                loader_class = DOCUMENT_LOADERS[file_ext]
                
                # Handle files differently based on storage location
                if settings.USE_MONGODB:
                    # Get file content from MongoDB and save to temp file
                    file_content = await get_file_from_mongodb(filename)
                    if file_content:
                        temp_file_path = await get_temp_file_path(filename, file_content)
                        loader = loader_class(temp_file_path)
                    else:
                        update_progress(current_stage=f"Файл {filename} не найден в MongoDB")
                        continue
                else:
                    # Use file directly from filesystem
                    loader = loader_class(filename)
                
                file_documents = loader.load()
                documents.extend(file_documents)
                
                processed_files += 1
                update_progress(
                    processed_files=processed_files,
                    current_stage=f"Загружен файл: {os.path.basename(filename)}"
                )
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                update_progress(current_stage=f"Ошибка при загрузке файла {os.path.basename(filename)}: {str(e)}")
        
        # Обновляем информацию о документах
        update_progress(
            total_documents=len(documents), 
            current_stage="Разбиение документов на чанки"
        )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        chunked_documents = text_splitter.split_documents(documents)
        
        update_progress(
            total_documents=len(chunked_documents),
            current_stage="Загрузка модели эмбеддингов"
        )
        
        # Проверяем, есть ли документы для обработки
        if not chunked_documents:
            error_message = "Не удалось извлечь текст из документов. Список документов для векторизации пуст."
            print(error_message)
            update_progress(error=error_message)
            # Сбрасываем флаг is_processing и завершаем функцию
            await asyncio.sleep(1)
            update_progress(is_processing=False)
            return
        
        embeddings = OpenAIEmbeddings()
        
        update_progress(current_stage="Создание векторной базы данных")
        
        update_progress(processed_documents=len(chunked_documents) - 1)
        
        # Configure Chroma to use MongoDB or local storage
        if settings.USE_MONGODB:
            # Use MongoDB for storing vectors with Chroma's MongoDB integration
            from chromadb.config import Settings as ChromaSettings
            from langchain_mongodb import MongoDBAtlasVectorSearch
            from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

            # Initialize MongoDB for vector storage
            update_progress(current_stage="Инициализация MongoDB для хранения векторов")
            
            # Use Chroma with MongoDB
            db = Chroma.from_documents(
                documents=chunked_documents,
                embedding=embeddings,
                collection_name="RAG",
                client_settings=Settings(anonymized_telemetry=False),
                persist_directory=None  # No local persist directory when using MongoDB
            )
        else:
            # Use local filesystem
            db = Chroma.from_documents(
                documents=chunked_documents,
                embedding=embeddings,
                collection_name="RAG",
                client_settings=Settings(anonymized_telemetry=False),
                persist_directory=db_path
            )
        
        # Обновляем финальный статус
        update_progress(
            processed_documents=len(chunked_documents),
            current_stage="Обработка завершена",
            percent_complete=100
        )
        
        print("Documents db upload done")
        
        # Через 5 секунд сбросим флаг is_processing
        await asyncio.sleep(5)
        update_progress(is_processing=False)
        
    except Exception as e:
        error_message = f"Ошибка при обработке: {str(e)}"
        print(error_message)
        update_progress(error=error_message)


