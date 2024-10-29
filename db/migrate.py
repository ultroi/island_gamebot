# db/migrate.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from config import DATABASE_PATH

def migrate_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Add max_health column if it doesn't exist
    cursor.execute("PRAGMA table_info(players);")
    columns = [column[1] for column in cursor.fetchall()]
    if 'max_health' not in columns:
        cursor.execute("ALTER TABLE players ADD COLUMN max_health INTEGER DEFAULT 100;")
        conn.commit()

    conn.close()

if __name__ == "__main__":
    migrate_db()