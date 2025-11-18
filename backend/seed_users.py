"""
Seed script to create initial users for the Diogenes Travel application
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test users to create
USERS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Admin User",
        "email": "admin@diogenes.com",
        "password": "admin123",
        "role": "admin"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Uçak Personeli",
        "email": "flight@diogenes.com",
        "password": "flight123",
        "role": "flight"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Rezervasyon Personeli",
        "email": "reservation@diogenes.com",
        "password": "reservation123",
        "role": "reservation"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Operasyon Personeli",
        "email": "operation@diogenes.com",
        "password": "operation123",
        "role": "operation"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Yönetim Personeli",
        "email": "management@diogenes.com",
        "password": "management123",
        "role": "management"
    }
]

async def seed_users():
    """Create initial users in the database"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    users_collection = db['users']
    
    # Check if users already exist
    existing_count = await users_collection.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Database already has {existing_count} users. Skipping seed.")
        return
    
    print("🌱 Seeding users...")
    
    for user_data in USERS:
        # Hash password
        hashed_password = pwd_context.hash(user_data["password"])
        
        # Create user document
        user_doc = {
            "id": user_data["id"],
            "name": user_data["name"],
            "email": user_data["email"],
            "password": hashed_password,
            "role": user_data["role"],
            "profile_picture": None
        }
        
        # Insert user
        await users_collection.insert_one(user_doc)
        print(f"✅ Created user: {user_data['name']} ({user_data['email']}) - Role: {user_data['role']}")
    
    print(f"\n🎉 Successfully seeded {len(USERS)} users!")
    print("\n📝 Login credentials:")
    print("-" * 60)
    for user in USERS:
        print(f"Email: {user['email']:<30} Password: {user['password']}")
    print("-" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_users())
