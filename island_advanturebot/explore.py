import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, CallbackContext
from shared import get_player


async def explore(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player = get_player(user_id)

    if player:
        events = [
            "You found a hidden cave with strange markings.",
            "You encountered a wild bear!",
            "You found an abandoned tribal village.",
            "You discovered an old temple with mystical powers.",
            "A peddler offers you supplies in exchange for resources."
        ]
        event = random.choice(events)
        
        response_text = f"🌍 **Exploration Event** 🌍\n\n{event}\n\nWhat will you do next?"
        explore_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Collect Resources", callback_data="collect_resources"),
             InlineKeyboardButton("Move On", callback_data="move_on")],
            [InlineKeyboardButton("Check Inventory", callback_data="check_inventory")]
        ])
        
        await update.message.reply_text(response_text, reply_markup=explore_buttons)
    else:
        await update.message.reply_text("You need to start the game with /start first.")
    context.chat_data  # Access chat data to ensure context is used


async def move_on(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    player = await get_player(user_id)  # Ensure this is called asynchronously

    if player:
        await explore(update)  # Call explore function asynchronously
    else:
        await update.callback_query.answer("You need to start the game with /start first.")
    context.chat_data  # Access chat data to ensure context is used


 
