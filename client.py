import logging
from pymongo import MongoClient, errors
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client("Island", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB Setup
mongo_client = MongoClient(MONGO_URI)

def setup_mongo():
    try:
        mongo_client.get_database()
        mongo_client.admin.command("ping")  # Ensure connection is valid
        logger.info("MongoDB connected successfully.")
        return mongo_client
    except errors.ConnectionFailure as e:
        logger.critical("Failed to connect to MongoDB", exc_info=True)
        raise e
