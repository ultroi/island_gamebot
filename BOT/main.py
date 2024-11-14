import logging
from pyrogram import Client, filters, idle
from BOT.config import MONGO_URI
from handlers.start_handler import start_command
from handlers.adventure_handler import explore_command
from handlers.inventory_handler import inv_command
from pymongo import MongoClient

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set up MongoDB connection
client = MongoClient(MONGO_URI)
db = client.get_database()

async def on_startup():
    # Perform any setup here
    logger.info("Bot has started and database connection is set up.")

BOT_TOKEN = "7882763921:AAE5LENSPtqmUvapKjS-byr1cBijcZ7N4oA"
API_ID = "6526942"
API_HASH = "3e0e31273667bfe888b1d140024aabdb"
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Register command handlers
app.add_handler(filters.command("start"), start_command)
app.add_handler(filters.command("explore"), explore_command)
app.add_handler(filters.command("inv"), inv_command)

# Start the bot and handle startup tasks
async def main():
    async with app:
        await on_startup()  # Call the startup function after the bot starts
        logging.info("Bot is running.")
        idle()

if __name__ == "__main__":
    import asyncio
    app.start()
    asyncio.run(main())
    logging.info("Bot is running.")
    app.stop()
