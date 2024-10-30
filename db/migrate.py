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
    column_names = [column[1] for column in cursor.fetchall()]
    if 'name' not in column_names:
        cursor.execute("""
            ALTER TABLE players 
            ADD COLUMN name TEXT;
        """)
    if 'max_health' not in column_names:
        cursor.execute("""
            ALTER TABLE players 
            ADD COLUMN max_health INTEGER DEFAULT 100;
        """)
    if 'explorations' not in column_names:
        cursor.execute("""
            ALTER TABLE players 
            ADD COLUMN explorations INTEGER DEFAULT 0;
        """)
    conn.commit()

    conn.close()

if __name__ == "__main__":
    migrate_db()