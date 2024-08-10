import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "ai_job_scraper")

# Lazy init to allow mongomock fallback
_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    if MONGO_URI:
        from pymongo import MongoClient
        _client = MongoClient(MONGO_URI)
        _db = _client[DB_NAME]
    else:
        # In-memory fallback for local dev without Mongo
        import mongomock
        _client = mongomock.MongoClient()
        _db = _client[DB_NAME]
    return _db

def jobs_collection():
    return get_db()["jobs"]

def upsert_jobs(jobs):
    col = jobs_collection()
    count = 0
    for job in jobs:
        res = col.update_one(
            {"source": job["source"], "source_id": job["source_id"]},
            {"$set": job},
            upsert=True
        )
        count += 1
    return count