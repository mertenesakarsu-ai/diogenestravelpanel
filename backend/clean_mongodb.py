"""
Clean test data from MongoDB - Keep only logs
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def clean_mongodb():
    """Remove all business data from MongoDB, keep only logs"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    mongo_client = AsyncIOMotorClient(mongo_url)
    mongo_db = mongo_client[os.environ['DB_NAME']]
    
    try:
        print("\n🧹 Cleaning MongoDB - Removing test/business data...")
        print("=" * 60)
        
        collections_to_clean = [
            'users',
            'flights', 
            'reservations', 
            'operations', 
            'hotels',
            'packages'
        ]
        
        total_deleted = 0
        
        for collection_name in collections_to_clean:
            collection = mongo_db[collection_name]
            count_before = await collection.count_documents({})
            
            if count_before > 0:
                result = await collection.delete_many({})
                print(f"  🗑️  {collection_name}: {result.deleted_count} records deleted")
                total_deleted += result.deleted_count
            else:
                print(f"  ✓  {collection_name}: Already empty")
        
        print("=" * 60)
        
        # Check logs
        logs_count = await mongo_db.logs.count_documents({})
        print(f"\n📊 MongoDB Status:")
        print(f"  - Business data deleted: {total_deleted} records")
        print(f"  - Logs kept: {logs_count} records")
        
        print("\n✅ MongoDB cleanup completed!")
        print("💡 MongoDB now only contains logs (as intended)")
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        raise
    finally:
        mongo_client.close()


if __name__ == "__main__":
    asyncio.run(clean_mongodb())
