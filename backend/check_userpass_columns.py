"""
Check UserPassControl table structure
"""
import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

SQL_HOST = os.getenv('SQL_SERVER_HOST')
SQL_PORT = int(os.getenv('SQL_SERVER_PORT', 1433))
SQL_USER = os.getenv('SQL_SERVER_USER')
SQL_PASSWORD = os.getenv('SQL_SERVER_PASSWORD')

try:
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
    print("USERPASSCONTROL TABLE STRUCTURE")
    print("=" * 80)
    
    # Get column information
    cursor.execute("""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'UserPassControl'
        ORDER BY ORDINAL_POSITION
    """)
    
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  - {col['COLUMN_NAME']}: {col['DATA_TYPE']} ({col['CHARACTER_MAXIMUM_LENGTH']})")
    
    # Get sample data
    print("\n" + "=" * 80)
    print("SAMPLE DATA (first 5 rows)")
    print("=" * 80 + "\n")
    
    cursor.execute("SELECT TOP 5 * FROM UserPassControl")
    rows = cursor.fetchall()
    
    for i, row in enumerate(rows, 1):
        print(f"Row {i}:")
        for key, value in row.items():
            if value is not None and len(str(value)) > 50:
                print(f"  {key}: {str(value)[:50]}... (truncated)")
            else:
                print(f"  {key}: {value}")
        print("-" * 40)
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
