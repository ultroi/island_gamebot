# utils/db_utils.py
from typing import Optional
from pymongo import MongoClient
from config import MONGO_URI
from models.player import Player
from pyrogram import Client

# Assuming you have a MongoDB client and database setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
players_collection = db.get_collection("players")

async def save_player(player: Player) -> None:
    try:
        players_collection.update_one(
            {'user_id': player.user_id},
            {'$set': {
                'name': player.name,
                'health': player.health,
                'max_health': player.max_health,
                'inventory': player.inventory,
                'location': player.location,
                'explorations': player.explorations,
                'experience': player.experience,
                'stamina': player.stamina
            }},
            upsert=True
        )
    except Exception as e:
        print(f"An error occurred while saving the player: {e}")

async def load_player(user_id: int) -> Optional[Player]:
    try:
        player_data = players_collection.find_one({'user_id': user_id})
        if player_data:
            return Player(
                user_id=player_data['user_id'],
                name=player_data['name'],
                health=player_data.get('health', 100),
                max_health=player_data.get('max_health', 100),
                inventory=player_data.get('inventory', []),
                location=player_data.get('location', 'beach'),
                explorations=player_data.get('explorations', 0),
                experience=player_data.get('experience', 0),
                stamina=player_data.get('stamina', 50)
            )
        return None
    except Exception as e:
        print(f"An error occurred while loading the player: {e}")
        return None

async def get_all_players():
    try:
        players_collection = db['players']
        players = list(players_collection.find())
        return players
    except Exception as e:
        print(f"An error occurred while retrieving players: {e}")
        return []

async def delete_player(user_id):
    try:
        players_collection = db['players']
        result = players_collection.delete_one({'user_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"An error occurred while deleting the player: {e}")
        return False

async def delete_player_progress(user_id, arc_type='survival', context=None):
    try:
        players_collection = db['players']
        if arc_type == 'survival':
            players_collection.delete_one({'user_id': user_id})
        # Add additional arc types as needed
    except Exception as e:
        print(f"An error occurred while deleting the player progress: {e}")