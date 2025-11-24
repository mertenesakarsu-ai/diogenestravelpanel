#!/usr/bin/env python3
"""
MongoDB Atlas Login Test
Tests if the backend can login with MongoDB Atlas
"""

import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def test_login():
    mongo_url = os.environ.get('MONGO_URL')
    db_name = os.environ.get('DB_NAME')
    
    print("🔍 MongoDB Atlas Login Testi")
    print(f"📦 Database: {db_name}")
    print()
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongo_url, server_api=ServerApi('1'))
    db = client[db_name]
    
    # Test credentials
    test_email = "admin@diogenestravel.com"
    test_password = "admin123"
    
    print(f"🔐 Test Kullanıcı: {test_email}")
    print(f"🔑 Şifre: {test_password}")
    print()
    
    # Find user
    user = await db.users.find_one({"email": test_email}, {"_id": 0})
    
    if not user:
        print("❌ Kullanıcı bulunamadı!")
        return False
    
    print(f"✅ Kullanıcı bulundu: {user.get('name')} ({user.get('role')})")
    print()
    
    # Verify password
    password_valid = pwd_context.verify(test_password, user['password'])
    
    if password_valid:
        print("✅ Şifre doğrulandı!")
        print()
        print("✅ Login başarılı!")
        print()
        print("👤 Kullanıcı Bilgileri:")
        print(f"   - ID: {user.get('id')}")
        print(f"   - İsim: {user.get('name')}")
        print(f"   - Email: {user.get('email')}")
        print(f"   - Rol: {user.get('role')}")
        print(f"   - Durum: {user.get('status')}")
        return True
    else:
        print("❌ Şifre yanlış!")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_login())
    exit(0 if result else 1)
