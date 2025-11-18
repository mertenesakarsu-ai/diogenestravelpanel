"""
Update existing user emails from @diogenes.com to @diogenestravel.com
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def update_emails():
    """Update all user emails from @diogenes.com to @diogenestravel.com"""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    users_collection = db['users']
    
    print("🔄 Updating user email addresses...")
    
    # Get all users with @diogenes.com email
    old_domain_users = await users_collection.find(
        {"email": {"$regex": "@diogenes\\.com$"}}
    ).to_list(length=None)
    
    if not old_domain_users:
        print("✅ No users found with @diogenes.com domain. All emails are up to date!")
        client.close()
        return
    
    print(f"Found {len(old_domain_users)} users to update:")
    
    updated_count = 0
    for user in old_domain_users:
        old_email = user['email']
        new_email = old_email.replace('@diogenes.com', '@diogenestravel.com')
        
        # Update the user
        result = await users_collection.update_one(
            {"id": user['id']},
            {"$set": {"email": new_email}}
        )
        
        if result.modified_count > 0:
            print(f"✅ Updated: {old_email} → {new_email}")
            updated_count += 1
        else:
            print(f"⚠️  Failed to update: {old_email}")
    
    print(f"\n🎉 Successfully updated {updated_count} user emails!")
    print("\n📝 New login credentials:")
    print("-" * 70)
    print(f"Admin:        admin@diogenestravel.com         / admin123")
    print(f"Flight:       flight@diogenestravel.com        / flight123")
    print(f"Reservation:  reservation@diogenestravel.com   / reservation123")
    print(f"Operation:    operation@diogenestravel.com     / operation123")
    print(f"Management:   management@diogenestravel.com    / management123")
    print("-" * 70)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_emails())
