from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from game_logic import gather_resources, craft_weapon, build_shelter, explore_forest, explore_cave
from multiplayer import create_group_command, join_group_command, leave_group_command, group_build_shelter_button
from utils import notify_player

# Global dictionary to track players who have entered the game world
player_states = {}

# Start command to greet the user
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to Survival Island Bot! Use /explore to start your adventure!")

# Explore command to initiate the game world and explore areas
def explore(update: Update, context: CallbackContext):
    player_id = update.message.from_user.id

    # Check if the player has already entered the game world
    if player_states.get(player_id):
        update.message.reply_text("You are already in the island world. You can explore different areas or gather resources.")
        # Call the exploration logic based on context
        return explore_environment(player_id)

    # Mark the player as having explored
    player_states[player_id] = True

    # Check if the player is part of a group
    group_name = context.user_data.get('group_name')  # Assuming group_name is stored in user_data
    if group_name:
        # Notify all group members
        notify_group_members(group_name, f"You and your team have entered the island world together!")
    else:
        update.message.reply_text("You have entered the island world alone. What will you do next?")
    
    # Initiate exploration logic
    return explore_environment(player_id)

def explore_environment(player_id):
    # Here you could implement logic to choose a random environment or let the player specify one
    # For simplicity, we will explore a forest or a cave randomly

    import random
    environment = random.choice(['forest', 'cave'])  # Randomly choose an environment

    if environment == 'forest':
        return explore_forest(player_id)  # Function to handle forest exploration
    elif environment == 'cave':
        return explore_cave(player_id)  # Function to handle cave exploration

def notify_group_members(group_name, message):
    # Placeholder function to notify all members of the group
    members = get_group_members(group_name)  # You need to implement this function
    for member in members:
        notify_player(member, message)

# Gather command to collect resources
def gather(update: Update, context: CallbackContext):
    player_id = update.message.from_user.id
    if not player_states.get(player_id):
        update.message.reply_text("You must first explore the island with /explore to enter the game world.")
        return
    gather_resources(player_id)

# Craft command to craft items
def craft(update: Update, context: CallbackContext):
    player_id = update.message.from_user.id
    if not player_states.get(player_id):
        update.message.reply_text("You must first explore the island with /explore to enter the game world.")
        return
    item_name = context.args[0] if context.args else None
    if item_name:
        craft_weapon(player_id, item_name)
    else:
        update.message.reply_text("Please specify an item to craft (e.g., /craft spear).")

# Build command to build a shelter
def build(update: Update, context: CallbackContext):
    player_id = update.message.from_user.id
    if not player_states.get(player_id):
        update.message.reply_text("You must first explore the island with /explore to enter the game world.")
        return
    build_shelter(player_id)

# Help command to explain available commands
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("""
    Here are the available commands:
    
    /explore - Start your adventure and explore different areas (e.g., forests, caves).
    /gather - Gather resources (wood, food, water) after exploring.
    /craft <item_name> - Craft weapons or items (e.g., /craft spear) after exploring.
    /build - Build or upgrade your personal shelter after exploring.
    /groupbuild - Collaborate with your group to build a communal shelter.
    /join_group <group_name> - Join an existing group (e.g., /join_group Warriors).
    /create_group <group_name> - Create a new group (e.g., /create_group Warriors).
    /leave_group <group_name> - Leave an existing group (e.g., /leave_group Warriors).
    /status - Check your current resources and status.

    Note: To play solo, simply use the above commands after exploring.
    """)

# Main function that sets up the bot
def main():
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your bot's token
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("explore", explore))  # Explore as the main initiation command
    dispatcher.add_handler(CommandHandler("gather", gather))
    dispatcher.add_handler(CommandHandler("craft", craft))
    dispatcher.add_handler(CommandHandler("build", build))
    dispatcher.add_handler(CommandHandler("groupbuild", group_build_shelter_button))
    dispatcher.add_handler(CommandHandler("create_group", create_group_command))
    dispatcher.add_handler(CommandHandler("join_group", join_group_command))
    dispatcher.add_handler(CommandHandler("leave_group", leave_group_command))

    # Start polling for updates
    updater.start_polling()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
