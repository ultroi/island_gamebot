# utils/db_utils.py
from db.database import get_db_connection
from models.player import Player
import sqlite3

def save_player(player):
    try:
        conn = get_db_connection()
        with conn:
            conn.execute(
                'INSERT OR REPLACE INTO players (user_id, name, health, max_health, inventory, location) VALUES (?, ?, ?, ?, ?, ?)',
                (player.user_id, player.name, player.health, player.max_health, ','.join(player.inventory), player.location)
            )
    except sqlite3.Error as e:
        print(f"An error occurred while saving the player: {e}")

def load_player(user_id):
    try:
        conn = get_db_connection()
        player_data = conn.execute('SELECT user_id, name, health, max_health, inventory, location FROM players WHERE user_id = ?', (user_id,)).fetchone()
        if player_data:
            return Player(
                user_id=player_data['user_id'],
                name=player_data['name'],
                health=player_data['health'],
                max_health=player_data['max_health'],
                inventory=player_data['inventory'].split(',') if player_data['inventory'] else [],
                location=player_data['location']
            )
        return None
    except sqlite3.Error as e:
        print(f"An error occurred while loading the player: {e}")
        return None

def get_all_players():
    try:
        conn = get_db_connection()
        players = conn.execute('SELECT * FROM players').fetchall()
        return players
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving players: {e}")
        return []

def delete_player(user_id):
    try:
        conn = get_db_connection()
        with conn:
            result = conn.execute('DELETE FROM players WHERE user_id = ?', (user_id,))
            return result.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred while deleting the player: {e}")
        return False
    

def delete_player_progress(user_id, arc_type='survival', context=None):
    try:
        conn = get_db_connection()
        with conn:
            if arc_type == 'survival':
                conn.execute('DELETE FROM players WHERE user_id = ?', (user_id,))
            # Add additional arc types as needed
    except sqlite3.Error as e:
        print(f"An error occurred while deleting the player progress: {e}")