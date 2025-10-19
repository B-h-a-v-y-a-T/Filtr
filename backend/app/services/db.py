import os
from typing import Optional, Dict, Any
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")

# MongoDB client and database
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None
analysis_collection: Optional[AsyncIOMotorCollection] = None


async def init_db() -> None:
    """Initialize MongoDB connection."""
    global mongo_client, mongo_db, analysis_collection
    
    if not DATABASE_URL:
        print("Warning: DATABASE_URL not configured")
        return
    
    try:
        mongo_client = AsyncIOMotorClient(DATABASE_URL)
        # Ping the database to verify connection
        await mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Get database name from URL or use default
        mongo_db = mongo_client.get_default_database()
        if mongo_db is None:
            # If no default database in URL, use 'stratosphere'
            mongo_db = mongo_client.stratosphere
        
        # Get collection for analysis records
        analysis_collection = mongo_db.analysis_records
        
        # Create indexes for better query performance
        await analysis_collection.create_index("input_type")
        await analysis_collection.create_index("created_at")
        
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        mongo_client = None
        mongo_db = None
        analysis_collection = None


async def close_db() -> None:
    """Close MongoDB connection."""
    global mongo_client
    if mongo_client:
        mongo_client.close()


async def create_analysis_record(input_type: str, payload: Dict[str, Any], result: Dict[str, Any]) -> Optional[str]:
    """
    Create a new analysis record in MongoDB.
    
    Args:
        input_type: Type of analysis (url, text, image, video)
        payload: Input payload
        result: Analysis result
    
    Returns:
        The inserted document ID as string, or None if DB not configured
    """
    if analysis_collection is None:
        return None
    
    try:
        document = {
            "input_type": input_type,
            "payload": payload,
            "result": result,
            "created_at": datetime.utcnow()
        }
        
        insert_result = await analysis_collection.insert_one(document)
        return str(insert_result.inserted_id)
    except Exception as e:
        print(f"Error creating analysis record: {e}")
        return None


async def get_analysis_records(limit: int = 100, skip: int = 0) -> list:
    """
    Retrieve analysis records from MongoDB.
    
    Args:
        limit: Maximum number of records to return
        skip: Number of records to skip
    
    Returns:
        List of analysis records
    """
    if analysis_collection is None:
        return []
    
    try:
        cursor = analysis_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        records = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for record in records:
            record["_id"] = str(record["_id"])
        
        return records
    except Exception as e:
        print(f"Error retrieving analysis records: {e}")
        return []







