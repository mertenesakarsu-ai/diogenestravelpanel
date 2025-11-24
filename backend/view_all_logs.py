#!/usr/bin/env python3
"""View all logs in MongoDB Atlas"""

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

async def view_logs():
    """View all logs in MongoDB Atlas"""
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        print("🔗 Connecting to MongoDB Atlas...")
        
        # Create client
        client = AsyncIOMotorClient(
            mongo_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000
        )
        
        db = client[db_name]
        
        # Get all logs
        log_count = await db.logs.count_documents({})
        print(f"\n📊 Total logs in MongoDB Atlas: {log_count}\n")
        
        if log_count > 0:
            print("=" * 80)
            print("ALL LOG ENTRIES")
            print("=" * 80)
            
            logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(100)
            
            for i, log in enumerate(logs, 1):
                timestamp = log.get('timestamp')
                if isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    timestamp_str = str(timestamp)
                
                print(f"\n📝 Log #{i}")
                print(f"   ⏰ Time: {timestamp_str}")
                print(f"   👤 User: {log.get('user', 'N/A')}")
                print(f"   🎬 Action: {log.get('action', 'N/A')}")
                print(f"   📦 Entity: {log.get('entity', 'N/A')}")
                print(f"   🆔 Entity ID: {log.get('entityId', 'N/A')}")
                print(f"   📄 Details: {log.get('details', 'N/A')}")
        else:
            print("❌ No logs found in database")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(view_logs())
    exit(0 if result else 1)
