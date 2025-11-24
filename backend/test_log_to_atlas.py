#!/usr/bin/env python3
"""Test logging to MongoDB Atlas"""

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone
import uuid

# Load environment variables
load_dotenv()

async def test_logging():
    """Test logging to MongoDB Atlas"""
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
        
        db = client[db_name]
        
        # Create a test log entry
        test_log = {
            "id": str(uuid.uuid4()),
            "user": "test@diogenestravel.com",
            "action": "TEST_CONNECTION",
            "entity": "system",
            "entityId": "test",
            "details": "Testing MongoDB Atlas connection and logging",
            "timestamp": datetime.now(timezone.utc)
        }
        
        print("\n📝 Writing test log to MongoDB Atlas...")
        result = await db.logs.insert_one(test_log)
        print(f"✅ Log written successfully! ID: {result.inserted_id}")
        
        # Verify the log was written
        log_count = await db.logs.count_documents({})
        print(f"📊 Total logs in database: {log_count}")
        
        # Read back the log
        latest_log = await db.logs.find_one({}, sort=[("timestamp", -1)])
        if latest_log:
            print(f"\n📖 Latest log entry:")
            print(f"   User: {latest_log.get('user')}")
            print(f"   Action: {latest_log.get('action')}")
            print(f"   Details: {latest_log.get('details')}")
            print(f"   Timestamp: {latest_log.get('timestamp')}")
        
        client.close()
        print("\n✅ All tests passed! MongoDB Atlas logging is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_logging())
    exit(0 if result else 1)
