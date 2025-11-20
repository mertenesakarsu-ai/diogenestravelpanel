"""
Check users in DIOGENESSEJOUR database (SejourPPUsers table)
and migrate them to diogenesDB users table with bcrypt passwords
"""
import pymssql
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# SQL Server configuration
SQL_HOST = os.getenv('SQL_SERVER_HOST')
SQL_PORT = int(os.getenv('SQL_SERVER_PORT', 1433))
SQL_USER = os.getenv('SQL_SERVER_USER')
SQL_PASSWORD = os.getenv('SQL_SERVER_PASSWORD')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_sejour_users():
    """Check users in DIOGENESSEJOUR database"""
    try:
        # Connect to DIOGENESSEJOUR database
        conn = pymssql.connect(
            server=SQL_HOST,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='DIOGENESSEJOUR',
            port=SQL_PORT,
            as_dict=True
        )
        cursor = conn.cursor()
        
        print("=" * 80)
        print("CHECKING SEJOUR USERS IN DIOGENESSEJOUR DATABASE")
        print("=" * 80)
        
        # Get SejourPPUsers
        cursor.execute("SELECT * FROM SejourPPUsers")
        users = cursor.fetchall()
        
        print(f"\nFound {len(users)} users in SejourPPUsers table:\n")
        
        for user in users:
            print(f"RecID: {user.get('RecID')}")
            print(f"  UserID: {user.get('UserID')}")
            print(f"  JoinedGrps: {user.get('JoinedGrps')}")
            print(f"  Status: {user.get('Status')}")
            print(f"  UserNote: {user.get('UserNote')}")
            print("-" * 40)
        
        # Check UserPassControl for passwords
        print("\n" + "=" * 80)
        print("CHECKING USER PASSWORDS IN UserPassControl")
        print("=" * 80)
        
        cursor.execute("SELECT * FROM UserPassControl")
        passwords = cursor.fetchall()
        
        print(f"\nFound {len(passwords)} entries in UserPassControl table:\n")
        
        for pwd in passwords:
            print(f"User: {pwd.get('User', 'N/A')}")
            print(f"  UserName: {pwd.get('UserName', 'N/A')}")
            print(f"  Password: {pwd.get('Password', 'N/A')[:20]}... (truncated)")
            print("-" * 40)
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def migrate_users_to_diogenesdb():
    """Migrate SejourPPUsers to diogenesDB users table"""
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
        print("MIGRATING SEJOUR USERS TO diogenesDB")
        print("=" * 80)
        
        # Get users from SejourPPUsers
        cursor_source.execute("SELECT * FROM SejourPPUsers")
        sejour_users = cursor_source.fetchall()
        
        # Get passwords from UserPassControl
        cursor_source.execute("SELECT * FROM UserPassControl")
        user_passwords = {pwd['User']: pwd['Password'] for pwd in cursor_source.fetchall()}
        
        # Get existing users in target database
        cursor_target.execute("SELECT email FROM users")
        existing_emails = [row['email'] for row in cursor_target.fetchall()]
        
        print(f"\nFound {len(sejour_users)} users in SejourPPUsers")
        print(f"Found {len(existing_emails)} existing users in diogenesDB\n")
        
        # Role mapping (you can adjust this based on JoinedGrps)
        role_mapping = {
            'ADMIN': 'admin',
            'EMRE': 'operation',
            'GOKCIN': 'reservation',
            'HALIT': 'flight',
            'GOKCE': 'management'
        }
        
        migrated_count = 0
        
        for user in sejour_users:
            user_id = user.get('UserID', '').strip()
            if not user_id:
                continue
                
            email = f"{user_id.lower()}@diogenestravel.com"
            
            # Skip if already exists
            if email in existing_emails:
                print(f"SKIPPED: {email} - already exists")
                continue
            
            # Get role
            role = role_mapping.get(user_id.upper(), 'operation')
            
            # Get password or use default
            raw_password = user_passwords.get(user_id, f"{user_id.lower()}123")
            hashed_password = pwd_context.hash(raw_password)
            
            # Generate UUID
            import uuid
            user_uuid = str(uuid.uuid4())
            
            # Insert user
            try:
                cursor_target.execute("""
                    INSERT INTO users (id, name, email, password, role, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, GETDATE())
                """, (user_uuid, user_id, email, hashed_password, role, 'active'))
                
                conn_target.commit()
                print(f"✅ MIGRATED: {email} - Role: {role}")
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ ERROR migrating {email}: {e}")
        
        conn_source.close()
        conn_target.close()
        
        print("\n" + "=" * 80)
        print(f"MIGRATION COMPLETE - {migrated_count} users migrated")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def ensure_default_users():
    """Ensure our 5 default users exist in diogenesDB"""
    try:
        conn = pymssql.connect(
            server=SQL_HOST,
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='diogenesDB',
            port=SQL_PORT,
            as_dict=True
        )
        cursor = conn.cursor()
        
        print("=" * 80)
        print("ENSURING DEFAULT USERS IN diogenesDB")
        print("=" * 80)
        
        default_users = [
            {
                'name': 'Admin',
                'email': 'admin@diogenestravel.com',
                'password': 'admin123',
                'role': 'admin'
            },
            {
                'name': 'Rezervasyon Manager',
                'email': 'reservation@diogenestravel.com',
                'password': 'reservation123',
                'role': 'reservation'
            },
            {
                'name': 'Operasyon Manager',
                'email': 'operation@diogenestravel.com',
                'password': 'operation123',
                'role': 'operation'
            },
            {
                'name': 'Uçak Manager',
                'email': 'flight@diogenestravel.com',
                'password': 'flight123',
                'role': 'flight'
            },
            {
                'name': 'Yönetim Manager',
                'email': 'management@diogenestravel.com',
                'password': 'management123',
                'role': 'management'
            }
        ]
        
        # Get existing users
        cursor.execute("SELECT email FROM users")
        existing_emails = [row['email'] for row in cursor.fetchall()]
        
        added_count = 0
        
        for user in default_users:
            if user['email'] in existing_emails:
                print(f"EXISTS: {user['email']}")
                continue
            
            # Hash password
            hashed_password = pwd_context.hash(user['password'])
            
            # Generate UUID
            import uuid
            user_uuid = str(uuid.uuid4())
            
            try:
                cursor.execute("""
                    INSERT INTO users (id, name, email, password, role, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, GETDATE())
                """, (user_uuid, user['name'], user['email'], hashed_password, user['role'], 'active'))
                
                conn.commit()
                print(f"✅ ADDED: {user['email']} - Role: {user['role']}")
                added_count += 1
                
            except Exception as e:
                print(f"❌ ERROR adding {user['email']}: {e}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print(f"DEFAULT USERS CHECK COMPLETE - {added_count} users added")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "SEJOUR USER MIGRATION TOOL" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # Step 1: Check SejourPPUsers
    check_sejour_users()
    
    print("\n\n")
    input("Press Enter to continue with migration...")
    print("\n")
    
    # Step 2: Migrate users
    migrate_users_to_diogenesdb()
    
    print("\n\n")
    input("Press Enter to ensure default users...")
    print("\n")
    
    # Step 3: Ensure default users
    ensure_default_users()
    
    print("\n\n✅ ALL DONE!\n")
