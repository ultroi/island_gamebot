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
from handlers.error_handler import global_exception_handler
from config import OWNER_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Startup tasks for the bot
async def on_startup():
    """
    This function runs tasks needed during bot startup.
    """
    logger.info("Bot startup tasks are executing...")
    # Add any additional startup logic here (e.g., cache loading, sending notifications)
    logger.info("Bot has started successfully.")

# Function to register all handlers
def register_handlers(app):
    """
    Registers all bot handlers.
    """
    try:
        logger.info("Registering bot handlers...")
        start_handler.register(app)
        adventure_handler.register(app)
        inventory_handler.register(app)
        dev_handler.register(app)
        callback_handler.register(app)
        logger.info("Handlers registered successfully.")
    except Exception as e:
        logger.error("Error while registering handlers.", exc_info=True)
        raise

# Main bot function
def main():
    """
    Main function to initialize and run the bot.
    """
    try:
        logger.info("Initializing bot...")

        # Create asyncio event loop and set global exception handler
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(global_exception_handler)

        # Setup MongoDB connection
        logger.info("Setting up MongoDB...")
        setup_mongo()
        logger.info("MongoDB setup completed.")

        # Register handlers
        register_handlers(app)

        # Asynchronous bot startup logic
        async def start_bot():
            async with app:
                await on_startup()
                logger.info("Bot is now running.")
                await idle()  # Keeps the bot running

        # Start the bot asynchronously
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        logger.warning("Bot stopped manually.")
    except Exception as e:
        logger.critical("Critical error occurred during bot startup.", exc_info=True)
    finally:
        logger.info("Shutting down bot...")
        asyncio.get_event_loop().stop()

# Entry point of the bot
if __name__ == "__main__":
    main()
