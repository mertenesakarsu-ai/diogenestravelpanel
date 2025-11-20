"""
Migrate users from MongoDB to SQL Server
"""
import asyncio
import pymssql
import os
from dotenv import load_dotenv
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def migrate_users():
    """Migrate all users from MongoDB to SQL Server"""
    
    # MongoDB connection
    mongo_url = os.environ['MONGO_URL']
    mongo_client = AsyncIOMotorClient(mongo_url)
    mongo_db = mongo_client[os.environ['DB_NAME']]
    
    # SQL Server connection
    sql_conn = pymssql.connect(
        server=os.environ['SQL_SERVER_HOST'],
        port=int(os.environ['SQL_SERVER_PORT']),
        user=os.environ['SQL_SERVER_USER'],
        password=os.environ['SQL_SERVER_PASSWORD'],
        database=os.environ['SQL_SERVER_DB'],
        autocommit=False
    )
    
    try:
        # Get all users from MongoDB
        users = await mongo_db.users.find().to_list(length=None)
        
        print(f"\n📊 Found {len(users)} users in MongoDB")
        print("=" * 60)
        
        if len(users) == 0:
            print("⚠️  No users found in MongoDB to migrate")
            return
        
        cursor = sql_conn.cursor()
        migrated_count = 0
        
        for user in users:
            user_id = user.get('id', '')
            name = user.get('name', '')
            email = user.get('email', '')
            password = user.get('password', '')
            role = user.get('role', '')
            status = user.get('status', 'active')
            profile_picture = user.get('profile_picture')
            created_at = user.get('created_at')
            
            try:
                # Insert into SQL Server
                cursor.execute("""
                    INSERT INTO users (id, name, email, password, role, status, profile_picture, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, name, email, password, role, status, profile_picture, created_at))
                
                print(f"  ✅ Migrated: {email} ({role})")
                migrated_count += 1
                
            except Exception as e:
                if "duplicate key" in str(e).lower() or "unique constraint" in str(e).lower():
                    print(f"  ⚠️  Already exists: {email}")
                else:
                    print(f"  ❌ Error migrating {email}: {e}")
        
        # Commit all changes
        sql_conn.commit()
        
        print("=" * 60)
        print(f"\n✅ Migration completed: {migrated_count} users migrated to SQL Server")
        
        # Verify in SQL Server
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"📊 Total users in SQL Server: {count}")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sql_conn.rollback()
        raise
    finally:
        sql_conn.close()
        mongo_client.close()


if __name__ == "__main__":
    asyncio.run(migrate_users())
