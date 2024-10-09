import aiosqlite
import logging

# Function to connect to the SQLite database
async def get_db_connection():
    logging.info("Connecting to the SQLite database...")
    return await aiosqlite.connect('island_tgbot.db')

# Function to set up the database
async def setup_db(conn):
    async with conn:
        cursor = await conn.cursor()
        await cursor.execute('''CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            health INTEGER,
            reputation INTEGER,
            inventory TEXT,
            resources TEXT,
            location TEXT,
            story_progress TEXT
        )''')
        await conn.commit()  # Commit after creating the table

async def create_player(user_id):
    conn = await get_db_connection()
    try:
        existing_player = await get_player(user_id)
        if existing_player:
            logging.info(f"Player with user_id {user_id} already exists.")
            return
        
        cursor = await conn.cursor()
        await cursor.execute('''INSERT INTO players (user_id, health, reputation, inventory, resources, location, story_progress)
                                VALUES (?, 100, 0, ?, ?, ?, ?)''', (user_id, '', '', 'Beach', ''))
        await conn.commit()
        logging.info(f"Player created with user_id {user_id}.")
    except aiosqlite.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        await conn.close()

async def get_player(user_id):
    conn = await get_db_connection()
    try:
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
        player_data = await cursor.fetchone()
        if player_data is not None:
            return player_data
        else:
            logging.info(f"No player found with user_id {user_id}.")
            return None
    except aiosqlite.Error as e:
        logging.error(f"Database error: {e}")
        return None
    finally:
        await conn.close()  # Ensure conn is closed

# Function to update player data
async def update_player(user_id, field, value):
    conn = await get_db_connection()
    try:
        cursor = await conn.cursor()
        await cursor.execute(f'UPDATE players SET {field} = ? WHERE user_id = ?', (value, user_id))
        await conn.commit()
    except aiosqlite.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        await conn.close()
