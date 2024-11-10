# main.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext
from config import BOT_TOKEN, MONGO_URI
from pymongo import MongoClient
from handlers.start_handler import start, button
from handlers.adventure_handler import explore, callback_handler, check_inventory
from handlers.inventory_handler import inventory
from handlers.help_handler import help_command
from handlers.dev_handler import dev, delete_player_data
from utils.decorators import maintenance_mode_only

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Set up MongoDB connection
client = MongoClient(MONGO_URI)
db = client.get_database()

async def on_startup(application):
    # setup_db()  # Assuming setup_db initializes the database connection
    logger.info("Database has been set up.")

async def maintenance_command(update: Update, context: CallbackContext):
    # This function will be wrapped by the maintenance_mode_only decorator
    pass

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    # Add command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('explore', explore))
    application.add_handler(CommandHandler('inv', inventory))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('dev', dev))
    application.add_handler(CommandHandler('Checkinv', check_inventory))
    application.add_handler(CommandHandler('delete_player', delete_player_data))
    application.add_handler(CommandHandler("mmode", maintenance_mode_only(maintenance_command)))
    application.add_handler(CommandHandler("dmmode", maintenance_mode_only(maintenance_command)))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Run the bot with polling
    application.run_polling()

if __name__ == '__main__':
    main()