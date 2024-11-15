import logging
import asyncio
from pymongo import MongoClient
from pyrogram import Client, idle
from config import MONGO_URI, API_ID, API_HASH, BOT_TOKEN
from handlers import start_handler, adventure_handler, inventory_handler, dev_handler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set up MongoDB connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()

# Initialize Pyrogram client
app = Client("island_gamebot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to set up logging when bot starts
async def on_startup():
    logger.info("Bot has started, and the database connection is set up.")

# Register handlers
def register_handlers(app):
    start_handler.register(app)
    adventure_handler.register(app)
    inventory_handler.register(app)
    dev_handler.register(app)
    logger.info("Handlers have been registered.")

# Main function to run the bot
async def start_bot():
    async with app:
        await on_startup()      # Log bot startup
        register_handlers(app)   # Register all handlers
        logger.info("Bot is now running.")
        await idle()             # Keep the bot running

# Run the bot
if __name__ == "__main__":
    app.run(start_bot())
# In this snippet, we have a main.py file that initializes the Pyrogram client, sets up the MongoDB connection, and registers the handlers. The start_bot function is the main entry point for running the bot, where we first log the bot startup, register all handlers, and then start the bot with the idle method.