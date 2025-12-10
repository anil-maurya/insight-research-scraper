# Test MongoDB connection
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variable
MONGO_URI = os.getenv('MONGO_URI')

def test_mongodb_connection():
    try:
        # Create MongoDB client
        client = MongoClient(MONGO_URI)
        
        # Test connection by listing database names
        dbs = client.list_database_names()
        print("Successfully connected to MongoDB!")
        print("Available databases:", dbs)
        
        # Close connection
        client.close()
        return True
        
    except Exception as e:
        print("Failed to connect to MongoDB")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_mongodb_connection()