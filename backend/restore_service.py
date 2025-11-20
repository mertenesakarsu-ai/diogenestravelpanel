"""
SQL Server Restore Service
Handles .bak file restore from S3 to AWS RDS SQL Server
"""

import pymssql
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# SQL Server connection details
SQL_SERVER_HOST = os.environ['SQL_SERVER_HOST']
SQL_SERVER_PORT = int(os.environ['SQL_SERVER_PORT'])
SQL_SERVER_USER = os.environ['SQL_SERVER_USER']
SQL_SERVER_PASSWORD = os.environ['SQL_SERVER_PASSWORD']

# AWS details
AWS_S3_BUCKET = os.environ['AWS_S3_BUCKET']
AWS_IAM_ROLE_ARN = os.environ['AWS_IAM_ROLE_ARN']


def get_connection(database='master'):
    """Create SQL Server connection"""
    return pymssql.connect(
        server=SQL_SERVER_HOST,
        user=SQL_SERVER_USER,
        password=SQL_SERVER_PASSWORD,
        database=database,
        port=SQL_SERVER_PORT,
        autocommit=True
    )


def start_restore(s3_key: str, target_db_name: str = 'DIOGENESSEJOUR'):
    """
    Start restore process from S3 .bak file
    
    Args:
        s3_key: S3 object key (e.g., 'sql-backups/DIOGENESSEJOUR_26_02.bak')
        target_db_name: Target database name (default: DIOGENESSEJOUR)
    
    Returns:
        dict with task_id and status
    """
    try:
        conn = get_connection('master')
        cursor = conn.cursor()
        
        # Construct S3 ARN
        s3_arn = f"arn:aws:s3:::{AWS_S3_BUCKET}/{s3_key}"
        
        print(f"🔄 Starting restore from S3...")
        print(f"   S3 ARN: {s3_arn}")
        print(f"   Target DB: {target_db_name}")
        
        # Call RDS stored procedure to restore database
        # This procedure handles the S3 download and restore
        sql = """
        EXEC msdb.dbo.rds_restore_database 
            @restore_db_name=%s, 
            @s3_arn_to_restore_from=%s
        """
        
        cursor.execute(sql, (target_db_name, s3_arn))
        
        # Get task_id from the result
        row = cursor.fetchone()
        if row:
            task_id = row[0] if row else None
            print(f"✅ Restore task started! Task ID: {task_id}")
            
            cursor.close()
            conn.close()
            
            return {
                "success": True,
                "task_id": task_id,
                "message": f"Restore started for {target_db_name}",
                "s3_arn": s3_arn,
                "target_db": target_db_name
            }
        else:
            cursor.close()
            conn.close()
            return {
                "success": False,
                "message": "No task ID returned from restore procedure"
            }
            
    except Exception as e:
        print(f"❌ Error starting restore: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "error": traceback.format_exc()
        }


def check_restore_status(task_id: int = None):
    """
    Check restore task status
    
    Args:
        task_id: Optional task ID to check specific task
        
    Returns:
        list of restore tasks with their status
    """
    try:
        conn = get_connection('master')
        cursor = conn.cursor(as_dict=True)
        
        # Query restore task status using AWS RDS function
        if task_id:
            sql = """
            SELECT TOP 10
                task_id,
                task_type,
                database_name,
                '%' as [percent_complete],
                lifecycle,
                task_info,
                created_at,
                last_updated
            FROM msdb.dbo.rds_fn_task_status(NULL, 0)
            WHERE task_id = %s
            ORDER BY created_at DESC
            """
            cursor.execute(sql, (task_id,))
        else:
            # Get all restore tasks
            sql = """
            SELECT TOP 10
                task_id,
                task_type,
                database_name,
                '%' as [percent_complete],
                lifecycle,
                task_info,
                created_at,
                last_updated
            FROM msdb.dbo.rds_fn_task_status(NULL, 0)
            WHERE task_type = 'RESTORE_DB'
            ORDER BY created_at DESC
            """
            cursor.execute(sql)
        
        tasks = []
        for row in cursor:
            tasks.append({
                "task_id": row['task_id'],
                "task_type": row['task_type'],
                "database_name": row['database_name'],
                "lifecycle": row['lifecycle'],
                "task_info": row['task_info'],
                "created_at": str(row['created_at']) if row['created_at'] else None,
                "updated_at": str(row['last_updated']) if row['last_updated'] else None
            })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        print(f"❌ Error checking restore status: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "error": traceback.format_exc()
        }


def wait_for_restore(task_id: int, timeout: int = 600, poll_interval: int = 10):
    """
    Wait for restore to complete
    
    Args:
        task_id: Task ID to monitor
        timeout: Maximum wait time in seconds (default 600 = 10 minutes)
        poll_interval: Check interval in seconds (default 10)
        
    Returns:
        dict with final status
    """
    start_time = time.time()
    
    print(f"⏱️  Waiting for restore to complete (timeout: {timeout}s)...")
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > timeout:
            return {
                "success": False,
                "message": "Restore timeout",
                "elapsed_seconds": elapsed
            }
        
        # Check status
        status = check_restore_status(task_id)
        
        if not status['success']:
            return status
        
        if not status['tasks']:
            return {
                "success": False,
                "message": "Task not found"
            }
        
        task = status['tasks'][0]
        lifecycle = task['lifecycle']
        
        print(f"   [{int(elapsed)}s] Status: {lifecycle}")
        
        # Check if completed
        if lifecycle == 'SUCCESS':
            print(f"✅ Restore completed successfully!")
            return {
                "success": True,
                "message": "Restore completed",
                "task": task,
                "elapsed_seconds": elapsed
            }
        elif lifecycle in ['FAILED', 'CANCELLED', 'ERROR']:
            print(f"❌ Restore failed: {lifecycle}")
            return {
                "success": False,
                "message": f"Restore {lifecycle.lower()}",
                "task": task,
                "elapsed_seconds": elapsed
            }
        
        # Still in progress, wait and retry
        time.sleep(poll_interval)


def list_databases():
    """List all databases on SQL Server"""
    try:
        conn = get_connection('master')
        cursor = conn.cursor(as_dict=True)
        
        sql = """
        SELECT 
            name,
            database_id,
            create_date,
            state_desc,
            recovery_model_desc,
            compatibility_level
        FROM sys.databases
        WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb', 'rdsadmin')
        ORDER BY name
        """
        
        cursor.execute(sql)
        
        databases = []
        for row in cursor:
            databases.append({
                "name": row['name'],
                "database_id": row['database_id'],
                "create_date": str(row['create_date']) if row['create_date'] else None,
                "state": row['state_desc'],
                "recovery_model": row['recovery_model_desc'],
                "compatibility_level": row['compatibility_level']
            })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "databases": databases,
            "count": len(databases)
        }
        
    except Exception as e:
        print(f"❌ Error listing databases: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def get_database_tables(database_name: str):
    """Get all tables in a database"""
    try:
        conn = get_connection(database_name)
        cursor = conn.cursor(as_dict=True)
        
        sql = """
        SELECT 
            t.name AS table_name,
            s.name AS schema_name,
            p.rows AS row_count
        FROM sys.tables t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0, 1)
        ORDER BY t.name
        """
        
        cursor.execute(sql)
        
        tables = []
        for row in cursor:
            tables.append({
                "table_name": row['table_name'],
                "schema_name": row['schema_name'],
                "row_count": row['row_count'] or 0
            })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "database": database_name,
            "tables": tables,
            "count": len(tables)
        }
        
    except Exception as e:
        print(f"❌ Error getting tables: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def get_table_schema(database_name: str, table_name: str, schema_name: str = 'dbo'):
    """Get detailed schema for a table"""
    try:
        conn = get_connection(database_name)
        cursor = conn.cursor(as_dict=True)
        
        sql = """
        SELECT 
            c.name AS column_name,
            t.name AS data_type,
            c.max_length,
            c.precision,
            c.scale,
            c.is_nullable,
            c.is_identity,
            CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS is_primary_key,
            CASE WHEN fk.parent_column_id IS NOT NULL THEN 1 ELSE 0 END AS is_foreign_key,
            fk_ref.referenced_table AS foreign_key_table,
            fk_ref.referenced_column AS foreign_key_column
        FROM sys.columns c
        INNER JOIN sys.types t ON c.user_type_id = t.user_type_id
        LEFT JOIN (
            SELECT ic.object_id, ic.column_id
            FROM sys.index_columns ic
            INNER JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
            WHERE i.is_primary_key = 1
        ) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
        LEFT JOIN sys.foreign_key_columns fk ON c.object_id = fk.parent_object_id AND c.column_id = fk.parent_column_id
        LEFT JOIN (
            SELECT 
                fkc.parent_object_id,
                fkc.parent_column_id,
                OBJECT_NAME(fkc.referenced_object_id) AS referenced_table,
                COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS referenced_column
            FROM sys.foreign_key_columns fkc
        ) fk_ref ON c.object_id = fk_ref.parent_object_id AND c.column_id = fk_ref.parent_column_id
        WHERE c.object_id = OBJECT_ID(?)
        ORDER BY c.column_id
        """
        
        full_table_name = f"{schema_name}.{table_name}"
        cursor.execute(sql.replace('?', '%s'), (full_table_name,))
        
        columns = []
        for row in cursor:
            columns.append({
                "column_name": row['column_name'],
                "data_type": row['data_type'],
                "max_length": row['max_length'],
                "precision": row['precision'],
                "scale": row['scale'],
                "is_nullable": bool(row['is_nullable']),
                "is_identity": bool(row['is_identity']),
                "is_primary_key": bool(row['is_primary_key']),
                "is_foreign_key": bool(row['is_foreign_key']),
                "foreign_key_table": row['foreign_key_table'],
                "foreign_key_column": row['foreign_key_column']
            })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "database": database_name,
            "table": table_name,
            "schema": schema_name,
            "columns": columns,
            "count": len(columns)
        }
        
    except Exception as e:
        print(f"❌ Error getting table schema: {e}")
        return {
            "success": False,
            "message": str(e)
        }


if __name__ == "__main__":
    # Test connection
    print("Testing SQL Server connection...")
    result = list_databases()
    if result['success']:
        print(f"✅ Connected! Found {result['count']} databases:")
        for db in result['databases']:
            print(f"   - {db['name']} ({db['state']})")
