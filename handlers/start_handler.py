# handlers/start_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from models.player import Player
from utils.db_utils import save_player
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from handlers.adventure_handler import explore


START_MESSAGE = "Welcome to the bot! Here you can embark on an exciting adventure."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    player = Player(user_id)
    save_player(player)

    # Initial welcome message with Adventure button
    keyboard = [
        [InlineKeyboardButton("Start Adventure", callback_data='start_adventure')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(START_MESSAGE, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'start_adventure':
        # Edit message to show brief about the game with two options
        keyboard = [
            [InlineKeyboardButton("Solo Arc", callback_data='solo_arc')],
            [InlineKeyboardButton("Narrative Arc", callback_data='narrative_arc')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Here is a brief about the game. Choose your path:", reply_markup=reply_markup)
    
    elif query.data == 'narrative_arc':
        # Show coming soon message for Narrative Arc
        await query.message.reply_text(text="Coming Soon")
    
    elif query.data == 'solo_arc':
        # Start the explore command for Solo Arc
        await explore(update, context)

    elif query.data == 'explore_again':
        # Run the explore command again
        await explore(update, context)

