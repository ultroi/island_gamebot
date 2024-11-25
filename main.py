import asyncio
import logging
import traceback
from pyrogram import idle
from pyrogram import client as app
from client import setup_mongo 
from handlers import start_handler, inventory_handler, dev_handler, adventure_handler, callback_handler
from handlers.error_handler import global_exception_handler 

# Set up logging
logger = logging.getLogger(__name__)

# Bot Owner ID
OWNER_ID = 5956598856

# Bot startup tasks
async def on_startup():
    logger.info("Bot has started.")

# Register bot handlers
def register_handlers(app):
    start_handler.register(app)
    adventure_handler.register(app)
    inventory_handler.register(app)
    dev_handler.register(app)
    callback_handler.register(app)

# Run bot
def main():
    try:
        # Add global exception handling
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(global_exception_handler)

        # Setup MongoDB
        setup_mongo()

        # Register handlers
        register_handlers(app)

        # Run the bot
        async def start_bot():
            async with app:
                await on_startup()
                logger.info("Bot is running.")
                await idle()  # Keep the bot running

        # Start the bot asynchronously
        loop.run_until_complete(start_bot())
    except Exception as e:
        logger.critical("An error occurred while running the bot", exc_info=True)

if __name__ == "__main__":
    main()
