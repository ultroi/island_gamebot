import logging
from pymongo import MongoClient, errors
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI
import time

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client("Island", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB Setup
mongo_client = None

def setup_mongo(retries: int = 3, delay: int = 5):
    global mongo_client
    attempt = 0
    
    while attempt < retries:
        try:
            mongo_client = MongoClient(MONGO_URI)
            mongo_client.get_database()  # Check if connection is valid
            mongo_client.admin.command("ping")  # Ensure connection is active
            logger.info("MongoDB connected successfully.")
            return mongo_client
        except errors.ConnectionFailure as e:
            attempt += 1
            logger.error(f"MongoDB connection attempt {attempt} failed. Error: {e}")
            if attempt < retries:
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.critical("Failed to connect to MongoDB after multiple attempts.", exc_info=True)
                raise e
        except Exception as e:
            logger.critical(f"Unexpected error while connecting to MongoDB: {e}", exc_info=True)
            raise e

def close_mongo_connection():
    """Close MongoDB connection gracefully."""
    global mongo_client
    if mongo_client:
        try:
            mongo_client.close()
            logger.info("MongoDB connection closed.")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")

# Set up cleanup when the bot shuts down
import atexit
atexit.register(close_mongo_connection)

