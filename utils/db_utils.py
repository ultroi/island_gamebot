# utils/db_utils.py
from pymongo import MongoClient
from config import MONGO_URI
from models.player import Player

client = MongoClient(MONGO_URI)
db = client['Tgbotproject']

async def save_player(player):
    try:
        players = db.players
        players.update_one(
            {'user_id': player.user_id},
            {'$set': {
                'name': player.name,
                'health': player.health,
                'max_health': player.max_health,
                'inventory': player.inventory,
                'location': player.location
            }},
            upsert=True
        )
    except Exception as e:
        print(f"An error occurred while saving the player: {e}")

def load_player(user_id):
    try:
        players_collection = db['players']
        player_data = players_collection.find_one({'user_id': user_id})
        if player_data:
            return Player(
                user_id=player_data['user_id'],
                name=player_data['name'],
                health=player_data['health'],
                max_health=player_data['max_health'],
                inventory=player_data['inventory'],
                location=player_data['location']
            )
        return None
    except Exception as e:
        print(f"An error occurred while loading the player: {e}")
        return None

def get_all_players():
    try:
        players_collection = db['players']
        players = list(players_collection.find())
        return players
    except Exception as e:
        print(f"An error occurred while retrieving players: {e}")
        return []

def delete_player(user_id):
    try:
        players_collection = db['players']
        result = players_collection.delete_one({'user_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"An error occurred while deleting the player: {e}")
        return False

def delete_player_progress(user_id, arc_type='survival', context=None):
    try:
        players_collection = db['players']
        if arc_type == 'survival':
            players_collection.delete_one({'user_id': user_id})
        # Add additional arc types as needed
    except Exception as e:
        print(f"An error occurred while deleting the player progress: {e}")