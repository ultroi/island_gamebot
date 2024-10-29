# utils/db_utils.py
from db.database import get_db_connection
from models.player import Player

def save_player(player):
    conn = get_db_connection()
    with conn:
        conn.execute(
            'INSERT OR REPLACE INTO players (user_id, health, inventory, location) VALUES (?, ?, ?, ?)',
            (player.user_id, player.health, ','.join(player.inventory), player.location)
        )

def load_player(user_id):
    conn = get_db_connection()
    player_data = conn.execute('SELECT * FROM players WHERE user_id = ?', (user_id,)).fetchone()
    if player_data:
        return Player(
            user_id=player_data['user_id'],
            health=player_data['health'],
            inventory=player_data['inventory'].split(','),
            location=player_data['location']
        )
    return None