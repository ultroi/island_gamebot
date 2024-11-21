import logging
from typing import Optional
from pymongo import MongoClient, UpdateOne
from config import MONGO_URI
from models.player import Player
from pyrogram import Client

# Set up logging for better error tracking
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assuming you have a MongoDB client and database setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
players_collection = db.get_collection("players")

async def save_player(user_id: int, player_data: dict):
    try:
        # Using upsert to insert or update the player data in one operation
        result = players_collection.update_one(
            {"user_id": user_id},
            {"$set": player_data},
            upsert=True
        )
        if result.upserted_id:
            logger.info(f"Player data inserted for user_id={user_id}")
        else:
            logger.info(f"Player data updated for user_id={user_id}")
    except Exception as e:
        logger.error(f"Error saving player data for user_id={user_id}: {e}")

async def load_player(user_id: int) -> Optional[Player]:
    try:
        # Proceed to load the player data for non-bot users
        player_data = players_collection.find_one({'user_id': user_id})
        if player_data:
            return Player.from_dict(player_data)
        return None
    except Exception as e:
        logger.error(f"An error occurred while loading the player {user_id}: {e}")
        return None

async def get_all_players():
    try:
        players = list(players_collection.find())
        return [Player.from_dict(player) for player in players]
    except Exception as e:
        logger.error(f"An error occurred while retrieving all players: {e}")
        return []

async def delete_player(user_id: int) -> bool:
    try:
        result = players_collection.delete_one({'user_id': user_id})
        if result.deleted_count > 0:
            logger.info(f"Player with user_id={user_id} deleted successfully.")
            return True
        logger.warning(f"No player found with user_id={user_id} to delete.")
        return False
    except Exception as e:
        logger.error(f"An error occurred while deleting the player {user_id}: {e}")
        return False

async def delete_player_progress(user_id: int, arc_type: str = 'survival', context: Optional[dict] = None):
    try:
        # Handle different types of arc deletions
        if arc_type == 'solo':
            result = players_collection.delete_one({'user_id': user_id})
            if result.deleted_count > 0:
                logger.info(f"Solo player progress for user_id={user_id} deleted.")
            else:
                logger.warning(f"No solo progress found for user_id={user_id} to delete.")
        # You can add more conditions for different arc types if needed
        # elif arc_type == 'multiplayer':
        #     result = players_collection.delete_one({'user_id': user_id, 'arc_type': 'multiplayer'})
        #     if result.deleted_count > 0:
        #         logger.info(f"Multiplayer progress for user_id={user_id} deleted.")
        # Add more arc types as needed...
    except Exception as e:
        logger.error(f"An error occurred while deleting player progress for {user_id} in {arc_type}: {e}")
