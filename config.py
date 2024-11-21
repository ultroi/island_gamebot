import os
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Read sensitive information from environment variables
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://default_user:default_password@default.mongodb.net/default_db?retryWrites=true&w=majority")
API_ID = os.getenv("API_ID", "6526942")
API_HASH = os.getenv("API_HASH", "3e0e31273667bfe888b1d140024aabdb")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7882763921:AAFgi6VZWbCNDK8A2XA5YodN-ljAKMeOHAI")
OWNER_ID = os.getenv("OWNER_ID", "5956598856")

# MongoDB Connection
def validate_mongo_uri():
    if not MONGO_URI.startswith("mongodb+srv://"):
        logger.warning("MONGO_URI is not a valid MongoDB connection string.")
    else:
        logger.info("MongoDB URI loaded successfully.")

# Validate config values for completeness and accuracy
def validate_config():
    required_keys = [API_ID, API_HASH, BOT_TOKEN, MONGO_URI, OWNER_ID]
    for key in required_keys:
        if not key:
            logger.critical(f"Missing critical config value: {key}")
            raise ValueError(f"Missing critical config value: {key}")

    # MongoDB URI validation
    validate_mongo_uri()

# Run validation on the config when the script loads
validate_config()

