import sqlite3
import os
from supabase import create_client, Client

# Use the credentials from your app.py
SUPABASE_URL = "https://mihwjfgwjdkraxyceamj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1paHdqZmd3amRrcmF4eWNlYW1qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODU2NzgyNiwiZXhwIjoyMDk0MTQzODI2fQ.IGa0ajGxa1yR2KCDKUMkqCx-0SUnTHSvkHb5cdUZJNw"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def migrate():
    if not os.path.exists(DB_PATH):
        print("Error: Local SQLite database.db not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    tables = [
        'students', 
        'faculty', 
        'courses', 
        'notifications', 
        'disciplinary', 
        'attendance_records', 
        'od_requests', 
        'student_courses', 
        'chatbot_logs', 
        'blocked_users'
    ]

    for table in tables:
        print(f"Migrating {table}...")
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if len(rows) > 0:
                # Use upsert so we don't crash on duplicate primary keys (like student registration numbers)
                response = supabase.table(table).upsert(rows).execute()
                print(f"Successfully migrated {len(rows)} records into {table}.")
            else:
                print(f"Table {table} is empty, skipping.")
        except Exception as e:
            print(f"Failed to migrate table {table}. Error: {str(e)}")

    conn.close()
    print("\nMigration Complete!")

if __name__ == '__main__':
    migrate()
