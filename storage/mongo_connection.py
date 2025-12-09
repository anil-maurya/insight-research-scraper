# MongoDB connection handler
# mongo_connection.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "insights_db")

_client = None

def get_db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client[DB_NAME]

def insert_raw(documents):
    """
    documents: list of dicts
    """
    db = get_db()
    coll = db["raw_comments"]
    if isinstance(documents, list):
        coll.insert_many(documents)
    else:
        coll.insert_one(documents)
