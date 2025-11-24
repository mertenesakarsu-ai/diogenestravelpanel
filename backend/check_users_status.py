#!/usr/bin/env python3
"""Check users in both SQL Server and MongoDB Atlas"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Load environment variables
load_dotenv()

async def check_users():
    """Check users in both databases"""
    try:
        # SQL Server connection
        sql_host = os.environ['SQL_SERVER_HOST']
        sql_port = os.environ['SQL_SERVER_PORT']
        sql_db = os.environ['SQL_SERVER_DB']
        sql_user = os.environ['SQL_SERVER_USER']
        sql_password = os.environ['SQL_SERVER_PASSWORD']
        
        connection_string = f"mssql+pymssql://{sql_user}:{sql_password}@{sql_host}:{sql_port}/{sql_db}"
        engine = create_engine(connection_string)
        
        print("=" * 60)
        print("SQL SERVER - USERS")
        print("=" * 60)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, email, role, status FROM users ORDER BY role"))
            users = result.fetchall()
            
            if users:
                print(f"✅ Found {len(users)} users in SQL Server:\n")
                for user in users:
                    print(f"   📧 {user[2]}")
                    print(f"      👤 Name: {user[1]}")
                    print(f"      🎭 Role: {user[3]}")
                    print(f"      📊 Status: {user[4]}")
                    print()
            else:
                print("❌ No users found in SQL Server")
        
        # MongoDB Atlas connection
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(
            mongo_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000
        )
        
        db = client[db_name]
        
        print("=" * 60)
        print("MONGODB ATLAS - LOGS")
        print("=" * 60)
        
        log_count = await db.logs.count_documents({})
        print(f"📝 Total logs in MongoDB Atlas: {log_count}")
        
        if log_count > 0:
            latest_logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(5).to_list(5)
            print(f"\n🔍 Latest {len(latest_logs)} log entries:")
            for log in latest_logs:
                print(f"   • {log.get('action')} by {log.get('user')} - {log.get('details')[:50]}...")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE CHECK COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(check_users())
    exit(0 if result else 1)
