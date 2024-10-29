# main.py
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from db.database import setup_db
from handlers.start_handler import start, button
from handlers.adventure_handler import explore
from handlers.inventory_handler import inventory
from handlers.help_handler import help_command

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def on_startup(application):
    setup_db()
    logger.info("Database has been set up.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('explore', explore))
    application.add_handler(CommandHandler('inventory', inventory))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot with polling
    application.run_polling()

if __name__ == '__main__':
    main()