"""
Add SejourPPUsers from DIOGENESSEJOUR to diogenesDB users table
Keep the original 5 users and add the new ones
"""
import pymssql
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
import uuid

load_dotenv()

SQL_HOST = os.getenv('SQL_SERVER_HOST')
SQL_PORT = int(os.getenv('SQL_SERVER_PORT', 1433))
SQL_USER = os.getenv('SQL_SERVER_USER')
SQL_PASSWORD = os.getenv('SQL_SERVER_PASSWORD')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_sejour_users():
    """Add SejourPPUsers to diogenesDB users table"""
    try:
        # Connect to DIOGENESSEJOUR to get users
        conn_source = pymssql.connect(
            server=SQL_HOST,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='DIOGENESSEJOUR',
            port=SQL_PORT,
            as_dict=True
        )
        cursor_source = conn_source.cursor()
        
        # Connect to diogenesDB to insert users
        conn_target = pymssql.connect(
            server=SQL_HOST,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='diogenesDB',
            port=SQL_PORT,
            as_dict=True
        )
        cursor_target = conn_target.cursor()
        
        print("=" * 80)
        print("ADDING SEJOUR USERS TO diogenesDB")
        print("=" * 80)
        
        # Get users from SejourPPUsers
        cursor_source.execute("SELECT * FROM SejourPPUsers")
        sejour_users = cursor_source.fetchall()
        
        # Get existing users in target database
        cursor_target.execute("SELECT email FROM users")
        existing_emails = [row['email'] for row in cursor_target.fetchall()]
        
        print(f"\nFound {len(sejour_users)} users in SejourPPUsers (DIOGENESSEJOUR)")
        print(f"Found {len(existing_emails)} existing users in diogenesDB\n")
        print("Existing users:")
        for email in existing_emails:
            print(f"  - {email}")
        print()
        
        # Define users to add with their roles
        # Original 5 users (already in database, will be skipped):
        # - admin@diogenestravel.com
        # - reservation@diogenestravel.com
        # - operation@diogenestravel.com
        # - flight@diogenestravel.com
        # - management@diogenestravel.com
        
        # Mapping for SejourPPUsers
        sejour_user_mapping = {
            'ADMIN': {
                'email': 'sejouradmin@diogenestravel.com',
                'name': 'Sejour Admin',
                'role': 'admin',
                'password': 'admin123'
            },
            'EMRE': {
                'email': 'emre@diogenestravel.com',
                'name': 'Emre',
                'role': 'operation',
                'password': 'emre123'
            },
            'GOKCIN': {
                'email': 'gokcin@diogenestravel.com',
                'name': 'Gökçin',
                'role': 'reservation',
                'password': 'gokcin123'
            },
            'HALIT': {
                'email': 'halit@diogenestravel.com',
                'name': 'Halit',
                'role': 'flight',
                'password': 'halit123'
            },
            'GOKCE': {
                'email': 'gokce@diogenestravel.com',
                'name': 'Gökçe',
                'role': 'management',
                'password': 'gokce123'
            }
        }
        
        added_count = 0
        skipped_count = 0
        
        print("=" * 80)
        print("PROCESSING SEJOUR USERS")
        print("=" * 80 + "\n")
        
        for user in sejour_users:
            user_id = user.get('UserID', '').strip().upper()
            if not user_id or user_id not in sejour_user_mapping:
                print(f"⚠️  SKIPPED: {user_id} - not in mapping")
                skipped_count += 1
                continue
            
            user_info = sejour_user_mapping[user_id]
            email = user_info['email']
            
            # Skip if already exists
            if email in existing_emails:
                print(f"✓  EXISTS: {email} - already in database")
                skipped_count += 1
                continue
            
            # Hash password
            hashed_password = pwd_context.hash(user_info['password'])
            
            # Generate UUID
            user_uuid = str(uuid.uuid4())
            
            # Insert user
            try:
                cursor_target.execute("""
                    INSERT INTO users (id, name, email, password, role, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, GETDATE())
                """, (
                    user_uuid,
                    user_info['name'],
                    email,
                    hashed_password,
                    user_info['role'],
                    'active'
                ))
                
                conn_target.commit()
                print(f"✅ ADDED: {email}")
                print(f"   Name: {user_info['name']}")
                print(f"   Role: {user_info['role']}")
                print(f"   Password: {user_info['password']}")
                print()
                added_count += 1
                
            except Exception as e:
                print(f"❌ ERROR adding {email}: {e}")
                print()
        
        conn_source.close()
        conn_target.close()
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Added: {added_count} users")
        print(f"⚠️  Skipped: {skipped_count} users (already exist or not mapped)")
        print(f"📊 Total in database: {len(existing_emails) + added_count} users")
        print()
        
        if added_count > 0:
            print("NEW USERS LOGIN CREDENTIALS:")
            print("-" * 80)
            for user_id, info in sejour_user_mapping.items():
                if info['email'] not in existing_emails:
                    print(f"Email: {info['email']}")
                    print(f"Password: {info['password']}")
                    print(f"Role: {info['role']}")
                    print()
        
        print("=" * 80)
        print("MIGRATION COMPLETE ✅")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "SEJOUR USER MIGRATION" + " " * 36 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    add_sejour_users()
    
    print("\n✅ DONE!\n")
