"""
Initialize default users directly in SQL Server
"""
import pymssql
import os
from dotenv import load_dotenv
from pathlib import Path
from passlib.context import CryptContext
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_sql_users():
    """Create default users in SQL Server"""
    
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
        cursor = sql_conn.cursor()
        
        # Check existing users
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"⚠️  {count} users already exist in SQL Server")
            cursor.execute("SELECT email, role FROM users")
            existing = cursor.fetchall()
            print("\n📋 Existing users:")
            for email, role in existing:
                print(f"  - {email} ({role})")
            return
        
        print("\n🔧 Creating default users in SQL Server...")
        print("=" * 60)
        
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
        
        created_count = 0
        for user in default_users:
            try:
                cursor.execute("""
                    INSERT INTO users (id, name, email, password, role, status, profile_picture, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user['id'], 
                    user['name'], 
                    user['email'], 
                    user['password'], 
                    user['role'], 
                    user['status'], 
                    user['profile_picture'], 
                    user['created_at']
                ))
                
                print(f"  ✅ Created: {user['email']} ({user['role']})")
                created_count += 1
                
            except Exception as e:
                print(f"  ❌ Error creating {user['email']}: {e}")
        
        # Commit all changes
        sql_conn.commit()
        
        print("=" * 60)
        print(f"\n✅ Successfully created {created_count} users in SQL Server")
        
        # Verify
        cursor.execute("SELECT COUNT(*) FROM users")
        total = cursor.fetchone()[0]
        print(f"📊 Total users in SQL Server: {total}")
        
        cursor.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sql_conn.rollback()
        raise
    finally:
        sql_conn.close()


if __name__ == "__main__":
    init_sql_users()
