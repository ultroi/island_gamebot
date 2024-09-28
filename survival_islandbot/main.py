from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from game_logic import gather_resources, craft_weapon, build_shelter, explore_forest
from events import dangerous_animal_event
from multiplayer import group_build_shelter_button, handle_group_build_shelter
from utils import notify_player, send_message_with_buttons
from database import get_resources, get_group, get_group_members  # Assuming these functions exist in your database module

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
    /status - Check your status or group status
    /start - Start the game
    """)

# Command to check status with inline buttons
def status_command(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Group Status", callback_data='group_status')],
        [InlineKeyboardButton("Player Status", callback_data='player_status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose an option to check:", reply_markup=reply_markup)

# Handler for the status inline buttons
def handle_status(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    choice = query.data

    player_id = context.user_data.get('player_id')  # Assume player_id is stored in user_data

    if choice == 'group_status':
        group_status = get_group_status(player_id)  # Pass player_id to get the group status
        query.edit_message_text(text=group_status)
    elif choice == 'player_status':
        player_status = get_player_status(player_id)  # Fetch player status
        query.edit_message_text(text=player_status)

def get_group_status(player_id):
    """Fetches and formats the group status."""
    group_info = get_group(player_id)  # Get group details from the database
    if group_info:
        group_name = group_info['name']
        members = get_group_members(group_name)
        member_list = "\n".join(members) if members else "No members in the group."
        return f"Group Name: {group_name}\nMembers:\n{member_list}"
    return "You are not in any group."

def get_player_status(player_id):
    """Fetches and formats the player status."""
    resources = get_resources(player_id)
    if resources:
        return f"Your Resources:\nWood: {resources.get('wood', 0)}\nBerries: {resources.get('berries', 0)}\nFish: {resources.get('fish', 0)}\nShells: {resources.get('shells', 0)}"
    return "You have no resources."

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
    dispatcher.add_handler(CommandHandler("status", status_command))

    # CallbackQueryHandler to handle inline buttons in group building and random events
    dispatcher.add_handler(CallbackQueryHandler(handle_group_build_shelter, pattern='^build_group_'))
    dispatcher.add_handler(CallbackQueryHandler(dangerous_animal_event, pattern='^(fight|flee)$'))
    dispatcher.add_handler(CallbackQueryHandler(handle_status, pattern='^(group_status|player_status)$'))

    # Start polling for updates
    updater.start_polling()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
