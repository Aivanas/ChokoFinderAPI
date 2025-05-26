import os
import asyncio
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from services.mongodb_handler import save_file_to_mongodb

async def migrate_documents_to_mongodb():
    """Migrate documents from local filesystem to MongoDB"""
    print("Starting migration of documents from local filesystem to MongoDB...")
    
    # Check if docs directory exists
    if not os.path.exists(settings.DOCS_DIRECTORY):
        print(f"Documents directory '{settings.DOCS_DIRECTORY}' does not exist. No documents to migrate.")
        return
    
    # List all files in docs directory
    files = os.listdir(settings.DOCS_DIRECTORY)
    total_files = len(files)
    
    if total_files == 0:
        print("No documents found to migrate.")
        return
    
    print(f"Found {total_files} documents to migrate.")
    
    migrated_count = 0
    failed_count = 0
    
    for i, filename in enumerate(files):
        try:
            file_path = os.path.join(settings.DOCS_DIRECTORY, filename)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            # Read file content
            with open(file_path, "rb") as file:
                content = file.read()
            
            # Save to MongoDB
            await save_file_to_mongodb(filename, content)
            
            migrated_count += 1
            print(f"[{i+1}/{total_files}] Migrated: {filename}")
        except Exception as e:
            failed_count += 1
            print(f"[{i+1}/{total_files}] Error migrating {filename}: {str(e)}")
    
    print("\nMigration complete!")
    print(f"Successfully migrated: {migrated_count} documents")
    print(f"Failed to migrate: {failed_count} documents")
    print("\nNow set USE_MONGODB=True in your .env file or environment variables")
    print("You can keep your original documents in the Docs directory as backup")

if __name__ == "__main__":
    # Run the migration
    asyncio.run(migrate_documents_to_mongodb()) 