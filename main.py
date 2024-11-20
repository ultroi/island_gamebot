import logging
import asyncio
import traceback
from pymongo import MongoClient, errors
from pyrogram import Client, idle
from config import MONGO_URI, API_ID, API_HASH, BOT_TOKEN
from handlers import start_handler, inventory_handler, dev_handler, adventure_handler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Owner ID
OWNER_ID = 5956598856

# Custom log handler to send critical errors to the owner
async def send_error_to_owner(bot, message: str):
    try:
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"🚨 *Critical Error* 🚨\n\n```\n{message}\n```",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send error to owner: {e}")

class TelegramLogHandler(logging.Handler):
    """Custom log handler to send logs to the Telegram bot owner."""
    def __init__(self, bot, loop):
        super().__init__()
        self.bot = bot
        self.loop = loop

    def emit(self, record):
        log_entry = self.format(record)
        # Use run_coroutine_threadsafe to ensure the coroutine is scheduled on the correct event loop
        asyncio.run_coroutine_threadsafe(send_error_to_owner(self.bot, log_entry), self.loop)


# Initialize Pyrogram client
app = Client("GAMEBOT", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# MongoDB SetupP
mongo_client = MongoClient(MONGO_URI)

def setup_mongo():
    try:
        mongo_client.get_database()
        db = mongo_client.get_database()
        mongo_client.admin.command("ping")  # Ensure connection is valid
        logger.info("MongoDB connected successfully.")
        return mongo_client
    except errors.ConnectionFailure as e:
        logger.critical("Failed to connect to MongoDB", exc_info=True)
        raise e

# Bot startup tasks
async def on_startup():
    logger.info("Bot has started.")

# Register bot handlers
def register_handlers(app):
    start_handler.register(app)
    adventure_handler.register(app)
    inventory_handler.register(app)
    dev_handler.register(app)
    logger.info("Handlers have been registered.")

# Global exception handler for uncaught errors
def global_exception_handler(loop, context):
    exception = context.get("exception")
    logger.error("Uncaught exception", exc_info=exception)
    if exception:
        # Send exception to the owner asynchronously
        loop.create_task(send_error_to_owner(app, "".join(
            traceback.format_exception(type(exception), exception, exception.__traceback__)
        )))

# Run bot
def main():
    try:
        # Add global exception handling
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(global_exception_handler)

        setup_mongo()

        # Register handlers before starting the bot
        register_handlers(app)

        # Run the bot
        async def start_bot():
            async with app:
                await on_startup()
                # Add the Telegram log handler after the bot has started
                telegram_handler = TelegramLogHandler(app, loop)
                telegram_handler.setLevel(logging.ERROR)
                logger.addHandler(telegram_handler)

                logger.info("Bot is running.")
                await idle()  # Keep the bot running

        # Start the bot asynchronously
        loop.run_until_complete(start_bot())
    except Exception as e:
        logger.critical("An error occurred while running the bot", exc_info=True)


if __name__ == "__main__":
    main()
