import logging
from explore import *  # Ensure these functions are properly defined in explore.py
from craft_build import *  # Ensure these functions are properly defined in craft_build.py
from shared import get_player, update_player, create_player
from inventory import inventory, collect_resources, check_inventory
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize bot with your credentials
API_TOKEN = "7882763921:AAFOKwA_Uv4NxFOQIfb_LJfNitc8Cy-w04c"  # Use your actual token here
application = Application.builder().token(API_TOKEN).build()

print("Telegram Bot initialized successfully!")

# Command: /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    player = await get_player(user_id)  # Ensure get_player is async

    if not player:
        await create_player(user_id)  # Ensure create_player is async
        welcome_text = (
            "🌴 **Welcome to Island Survival Adventure!** 🌴\n\n"
            "You are stranded on a mysterious island. Your goal is to survive, explore, and uncover the island's secrets.\n"
            "Tap **'Let's Begin'** to start your adventure!"
        )
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Let's Begin", callback_data="begin_explore")]])
        await update.message.reply_text(welcome_text, reply_markup=buttons)
    else:
        await update.message.reply_text("You have already started your adventure. Use /explore to continue.")

# Handling the begin exploration
async def handle_begin_explore(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer("Adventure started!")  # Optional feedback
    
    user_id = query.from_user.id
    player = await get_player(user_id)

    # Set initial player location and resources
    if player:
        await update_player(user_id, "current_location", "beach")  # Assuming update_player is async
        initial_resources = "wood, stone"
        await update_player(user_id, "resources", initial_resources)  # Grant initial resources
        
        # Notify the player of their starting state
        await query.message.reply_text(
            "You find yourself on a sunny beach, surrounded by palm trees. You have some initial resources:\n"
            f"🔹 Resources: {initial_resources}\n"
            "What would you like to do next? Use /explore to start searching the island!"
        )

# Command: /check (to view player stats)
async def check_stats(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    player = await get_player(user_id)

    if player:
        health = player[1]  # Adjust indices as per your player data structure
        reputation = player[2]
        inventory_items = player[3] or "Empty"
        await update.message.reply_text(f"🧑‍🤝‍🧑 **Your Stats** 🧑‍🤝‍🧑\n\n"
                                  f"💪 Health: {health}\n"
                                  f"🤝 Reputation: {reputation}\n"
                                  f"🎒 Inventory: {inventory_items}")
    else:
        await update.message.reply_text("You need to start the game with /start first.")

# Command: /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("🤔 **Help** 🤔\n\n"
                              "Here are the commands you can use:\n"
                              "/start - Start your adventure\n"
                              "/explore - Explore the island\n"
                              "/craft - Craft items\n"
                              "/build - Build a shelter\n"
                              "/check - Check your stats\n"
                              "/help - Show this help message")

# Set up handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("craft", craft))  # Ensure craft is defined
application.add_handler(CommandHandler("build", build))  # Ensure build is defined
application.add_handler(CommandHandler("check", check_stats))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("inv", inventory))  # For inventory command
application.add_handler(CommandHandler("collect", collect_resources))  # For collecting resources
application.add_handler(CommandHandler("check_inventory", check_inventory))
application.add_handler(CallbackQueryHandler(handle_begin_explore, pattern="begin_explore"))
# Ensure this function is defined
application.add_handler(CallbackQueryHandler(handle_build_shelter, pattern=r'build_.*'))

# Start the bot
async def main():
    try:
        await application.initialize()  # Initialize the application
        await application.start_polling()  # Start polling for updates
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await application.shutdown()  # Ensure the application shuts down cleanly

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
