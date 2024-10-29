# utils/db_utils.py
from db.database import get_db_connection
from models.player import Player
import sqlite3

def save_player(player):
    try:
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT OR REPLACE INTO players (user_id, health, max_health, inventory, location) VALUES (?, ?, ?, ?, ?)',
                (player.user_id, player.health, player.max_health, ','.join(player.inventory), player.location)
            )
    except sqlite3.Error as e:
        print(f"An error occurred while saving the player: {e}")

def load_player(user_id):
    try:
        conn = get_db_connection()
        player_data = conn.execute('SELECT * FROM players WHERE user_id = ?', (user_id,)).fetchone()
        if player_data:
            return Player(
                user_id=player_data['user_id'],
                health=player_data['health'],
                max_health=player_data['max_health'],
                inventory=player_data['inventory'].split(','),
                location=player_data['location']
            )
        return None
    except sqlite3.Error as e:
        print(f"An error occurred while loading the player: {e}")
        return None