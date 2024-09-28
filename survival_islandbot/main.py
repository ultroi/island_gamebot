from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from game_logic import gather_resources, craft_weapon, build_shelter
from events import dangerous_animal_event, explore_forest
from multiplayer import group_build_shelter_button, handle_group_build_shelter
from utils import notify_player, send_message_with_buttons

# Start command to greet the user
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to Survival Island Bot! Use /gather to gather resources, /explore to explore the forest, or /groupbuild to collaborate with others!")

# Help command to explain available commands
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("""
    Here are the available commands:
    /gather - Gather resources (wood, food, water)
    /craft - Craft weapons or items
    /build - Build or upgrade your personal shelter
    /groupbuild - Collaborate with your group to build a communal shelter
    /explore - Explore the forest for random events or treasures
    /start - Start the game
    """)

# Main function that sets up the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot's token
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("gather", gather_resources))
    dispatcher.add_handler(CommandHandler("craft", craft_weapon))
    dispatcher.add_handler(CommandHandler("build", build_shelter))
    dispatcher.add_handler(CommandHandler("explore", explore_forest))
    dispatcher.add_handler(CommandHandler("groupbuild", group_build_shelter_button))
    
    # CallbackQueryHandler to handle inline buttons in group building and random events
    dispatcher.add_handler(CallbackQueryHandler(handle_group_build_shelter, pattern='^build_group_'))
    dispatcher.add_handler(CallbackQueryHandler(dangerous_animal_event, pattern='^(fight|flee)$'))

    # Start polling for updates
    updater.start_polling()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
