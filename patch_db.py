import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'database.db')
print(f"Patching DB at {DB_PATH}")

try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS chatbot_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        name TEXT,
        message TEXT,
        response TEXT,
        timestamp TEXT,
        is_unnecessary INTEGER DEFAULT 0
    );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS blocked_users (
        user_id TEXT PRIMARY KEY,
        role TEXT
    );
    ''')
    conn.commit()
    print("Database patching completed successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
