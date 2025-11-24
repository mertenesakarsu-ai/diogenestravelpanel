#!/usr/bin/env python3
"""Migrate users to MongoDB Atlas"""

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone
import uuid
from passlib.context import CryptContext

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_users():
    """Create default users in MongoDB Atlas"""
    try:
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        print("🔗 Connecting to MongoDB Atlas...")
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
        
        # Check if users already exist
        existing_count = await db.users.count_documents({})
        print(f"\n📊 Existing users in database: {existing_count}")
        
        if existing_count > 0:
            print("\n⚠️ Users already exist. Deleting old users...")
            await db.users.delete_many({})
            print("✅ Old users deleted")
        
        # Create default users
        default_users = [
            {
                "id": str(uuid.uuid4()),
                "name": "Admin User",
                "email": "admin@diogenestravel.com",
                "password": pwd_context.hash("admin123"),
                "role": "admin",
                "status": "active",
                "profile_picture": None,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Rezervasyon Manager",
                "email": "reservation@diogenestravel.com",
                "password": pwd_context.hash("reservation123"),
                "role": "reservation",
                "status": "active",
                "profile_picture": None,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Operasyon Manager",
                "email": "operation@diogenestravel.com",
                "password": pwd_context.hash("operation123"),
                "role": "operation",
                "status": "active",
                "profile_picture": None,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Uçak Manager",
                "email": "flight@diogenestravel.com",
                "password": pwd_context.hash("flight123"),
                "role": "flight",
                "status": "active",
                "profile_picture": None,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Yönetim Manager",
                "email": "management@diogenestravel.com",
                "password": pwd_context.hash("management123"),
                "role": "management",
                "status": "active",
                "profile_picture": None,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        print("\n📝 Creating users in MongoDB Atlas...")
        
        for user in default_users:
            await db.users.insert_one(user)
            print(f"✅ Created user: {user['email']} ({user['role']})")
        
        print(f"\n✅ Successfully created {len(default_users)} users in MongoDB Atlas!")
        
        # Verify
        final_count = await db.users.count_documents({})
        print(f"📊 Total users in database: {final_count}")
        
        # List all users
        print("\n" + "=" * 60)
        print("ALL USERS IN MONGODB ATLAS")
        print("=" * 60)
        
        users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(10)
        for user in users:
            print(f"\n👤 {user['name']}")
            print(f"   📧 Email: {user['email']}")
            print(f"   🎭 Role: {user['role']}")
            print(f"   📊 Status: {user['status']}")
        
        client.close()
        
        print("\n" + "=" * 60)
        print("✅ USER MIGRATION COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(create_users())
    exit(0 if result else 1)
