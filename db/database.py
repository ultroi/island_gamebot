# db/database.py
import sqlite3
from config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def setup_db():
    conn = get_db_connection()
    with open('db/schema.sql') as f:
        conn.executescript(f.read())
    conn.close()