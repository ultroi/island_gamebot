import asyncio
import logging
from pyrogram import idle
from client import app, setup_mongo  # Import client and MongoDB setup
from handlers import (
    start_handler,
    inventory_handler,
    dev_handler,
    adventure_handler,
    callback_handler,
)
from handlers.error_handler import global_exception_handler, error_handler_decorator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Global variable to store bot's ID
BOT_ID = 7882763921

async def fetch_bot_id():
    """
    Fetch and return the bot's ID.
    Assumes the client (app) is already running.
    """
    global BOT_ID
    bot_info = await app.get_me()
    BOT_ID = bot_info.id
    logger.info(f"Bot ID: {BOT_ID}")

async def on_startup():
    """
    This function runs tasks needed during bot startup.
    """
    logger.info("Executing bot startup tasks...")
    await fetch_bot_id()  # Ensure bot's ID is fetched before starting handlers
    logger.info("Bot startup tasks completed successfully.")

def register_handlers(app):
    """
    Registers all bot handlers.
    """
    try:
        logger.info("Registering bot handlers...")
        start_handler.register(app)
        adventure_handler.register(app)
        inventory_handler.register(app)  # Register inventory handler
        dev_handler.register(app)
        callback_handler.register(app)
        logger.info("Handlers registered successfully.")
    except Exception as e:
        logger.error("Error while registering handlers.", exc_info=True)
        raise

async def run_bot():
    """
    Main bot loop.
    """
    logger.info("Initializing bot...")

    # Create asyncio event loop and set global exception handler
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(global_exception_handler)

    # Setup MongoDB connection
    logger.info("Setting up MongoDB...")
    setup_mongo()
    logger.info("MongoDB setup completed.")

    try:
        async with app:  # Start the bot context here
            await on_startup()
            register_handlers(app)  # Register handlers after bot ID is fetched
            logger.info("Bot is now running.")
            await idle()  # Keeps the bot running
    except KeyboardInterrupt:
        logger.warning("Bot stopped manually.")
    except Exception as e:
        logger.critical("Critical error occurred during bot startup.", exc_info=True)
    finally:
        logger.info("Shutting down bot...")
        asyncio.get_event_loop().stop()

def main():
    """
    Entry point for bot execution.
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())

# Entry point of the bot
if __name__ == "__main__":
    main()
