import os
import sys
import dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_mongodb_connection():
    """Setup MongoDB connection details and save them to .env file"""
    print("=== MongoDB Configuration Setup ===")
    print("\nThis script will help you configure MongoDB connection settings.")
    print("It will update your .env file with the new settings.\n")
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if not os.path.exists(env_file):
        print("Creating new .env file...")
        with open(env_file, 'w') as f:
            f.write("# MongoDB Configuration\n")
    else:
        print("Updating existing .env file...")
    
    # Load existing .env file
    dotenv.load_dotenv(env_file)
    
    # Get MongoDB connection settings
    mongodb_url = input("MongoDB Connection URL [mongodb://localhost:27017]: ").strip()
    if not mongodb_url:
        mongodb_url = "mongodb://localhost:27017"
    
    mongodb_db_name = input("MongoDB Database Name [chokofinder]: ").strip()
    if not mongodb_db_name:
        mongodb_db_name = "chokofinder"
    
    mongodb_collection_name = input("MongoDB Collection Name [documents]: ").strip()
    if not mongodb_collection_name:
        mongodb_collection_name = "documents"
    
    # Set USE_MONGODB to true
    use_mongodb = "true"
    
    # Update .env file
    dotenv.set_key(env_file, "MONGODB_URL", mongodb_url)
    dotenv.set_key(env_file, "MONGODB_DB_NAME", mongodb_db_name)
    dotenv.set_key(env_file, "MONGODB_COLLECTION_NAME", mongodb_collection_name)
    dotenv.set_key(env_file, "USE_MONGODB", use_mongodb)
    
    print("\nMongoDB configuration has been saved to .env file.")
    print(f"MongoDB URL: {mongodb_url}")
    print(f"Database Name: {mongodb_db_name}")
    print(f"Collection Name: {mongodb_collection_name}")
    print(f"USE_MONGODB: {use_mongodb}")
    
    print("\nTo migrate your existing documents to MongoDB, run the following command:")
    print("python tools/migrate_to_mongodb.py")
    
    print("\nTo start using MongoDB for document storage, restart your application:")
    print("uvicorn main:app --reload")

if __name__ == "__main__":
    setup_mongodb_connection() 