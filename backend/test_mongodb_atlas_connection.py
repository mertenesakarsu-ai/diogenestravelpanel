#!/usr/bin/env python3
"""Test MongoDB Atlas connection"""

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Load environment variables
load_dotenv()

async def test_connection():
    """Test MongoDB Atlas connection"""
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        print(f"🔗 Connecting to MongoDB Atlas...")
        print(f"📊 Database: {db_name}")
        
        # Create client
        client = AsyncIOMotorClient(
            mongo_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000
        )
        
        # Test connection by pinging the database
        db = client[db_name]
        await db.command('ping')
        
        print("✅ MongoDB Atlas connection successful!")
        
        # Get collection stats
        collections = await db.list_collection_names()
        print(f"📂 Available collections: {collections if collections else 'None (empty database)'}")
        
        # If logs collection exists, show count
        if 'logs' in collections:
            log_count = await db.logs.count_documents({})
            print(f"📝 Total logs in database: {log_count}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
