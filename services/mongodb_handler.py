import motor.motor_asyncio
from pymongo import MongoClient
from bson.binary import Binary
import io
import os
from config import settings
from core.progress import update_progress

# Singleton MongoDB clients
_async_client = None
_sync_client = None

def get_async_client():
    """Get or create the async MongoDB client"""
    global _async_client
    if _async_client is None:
        _async_client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    return _async_client

def get_sync_client():
    """Get or create the sync MongoDB client"""
    global _sync_client
    if _sync_client is None:
        _sync_client = MongoClient(settings.MONGODB_URL)
    return _sync_client

async def save_file_to_mongodb(filename, file_content):
    """Save a file to MongoDB"""
    client = get_async_client()
    db = client[settings.MONGODB_DB_NAME]
    collection = db[settings.MONGODB_COLLECTION_NAME]
    
    # Check if file already exists
    existing = await collection.find_one({"filename": filename})
    if existing:
        # Update existing document
        await collection.update_one(
            {"filename": filename},
            {"$set": {"content": Binary(file_content)}}
        )
    else:
        # Create new document
        doc = {
            "filename": filename,
            "content": Binary(file_content),
            "metadata": {
                "type": os.path.splitext(filename)[1].lower(),
                "size": len(file_content)
            }
        }
        await collection.insert_one(doc)
        
    return filename

async def get_file_from_mongodb(filename):
    """Retrieve a file from MongoDB"""
    client = get_async_client()
    db = client[settings.MONGODB_DB_NAME]
    collection = db[settings.MONGODB_COLLECTION_NAME]
    
    doc = await collection.find_one({"filename": filename})
    if not doc:
        return None
    
    return doc["content"]

async def delete_file_from_mongodb(filename):
    """Delete a file from MongoDB"""
    client = get_async_client()
    db = client[settings.MONGODB_DB_NAME]
    collection = db[settings.MONGODB_COLLECTION_NAME]
    
    result = await collection.delete_one({"filename": filename})
    return result.deleted_count > 0

async def list_files_from_mongodb():
    """List all files stored in MongoDB"""
    client = get_async_client()
    db = client[settings.MONGODB_DB_NAME]
    collection = db[settings.MONGODB_COLLECTION_NAME]
    
    cursor = collection.find({}, {"filename": 1, "_id": 0})
    files = await cursor.to_list(length=None)
    return [file["filename"] for file in files]

async def get_temp_file_path(filename, content=None):
    """
    Get or create a temporary file path for a file 
    that may be stored in MongoDB but needs local access
    """
    os.makedirs(settings.DOCS_DIRECTORY, exist_ok=True)
    temp_path = os.path.join(settings.DOCS_DIRECTORY, filename)
    
    # If content is provided, write it to the file
    if content:
        with open(temp_path, 'wb') as f:
            f.write(content)
    
    return temp_path 