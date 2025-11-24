#!/usr/bin/env python3
"""Test login and check if logs are written to MongoDB Atlas"""

import requests
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def check_logs():
    """Check MongoDB Atlas logs"""
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
    
    # Get recent logs
    logs = await db.logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(10).to_list(10)
    
    client.close()
    return logs

def test_login():
    """Test login via API"""
    url = "https://flight-data-hub.preview.emergentagent.com/api/login"
    
    print("=" * 60)
    print("TESTING LOGIN API")
    print("=" * 60)
    
    # Test 1: Valid login
    print("\n📝 Test 1: Valid admin login")
    payload = {
        "email": "admin@diogenestravel.com",
        "password": "admin123"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Login successful!")
        print(f"   Name: {user_data.get('name')}")
        print(f"   Email: {user_data.get('email')}")
        print(f"   Role: {user_data.get('role')}")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 2: Invalid login
    print("\n📝 Test 2: Invalid login (wrong password)")
    payload = {
        "email": "admin@diogenestravel.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 401:
        print(f"✅ Correctly rejected invalid login")
    else:
        print(f"⚠️ Unexpected response: {response.status_code}")

async def main():
    """Main test function"""
    # Test login
    test_login()
    
    # Wait a bit for logs to be written
    print("\n⏳ Waiting for logs to be written...")
    await asyncio.sleep(2)
    
    # Check logs
    print("\n" + "=" * 60)
    print("CHECKING MONGODB ATLAS LOGS")
    print("=" * 60)
    
    logs = await check_logs()
    
    print(f"\n📊 Found {len(logs)} recent log entries:\n")
    
    login_logs = [log for log in logs if 'LOGIN' in log.get('action', '')]
    
    if login_logs:
        print(f"✅ Found {len(login_logs)} login-related logs:")
        for log in login_logs:
            print(f"\n   • Action: {log.get('action')}")
            print(f"     User: {log.get('user')}")
            print(f"     Details: {log.get('details')}")
            print(f"     Time: {log.get('timestamp')}")
    else:
        print("⚠️ No login logs found yet")
        print("\nAll recent logs:")
        for log in logs:
            print(f"   • {log.get('action')} by {log.get('user')}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
