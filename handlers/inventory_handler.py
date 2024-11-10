from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from utils.db_utils import load_player
from typing import Optional
from handlers.adventure_handler import get_player_status
from utils.decorators import user_verification, maintenance_mode_only


@user_verification
@maintenance_mode_only
async def inventory(update: Update) -> None:
    user_id = update.message.from_user.id
    player = load_player(user_id)
    
    if not player:
        await update.message.reply_text("You need to start your adventure first using /start.")
        return

    response_message = get_player_status(player)
    
    # Creating inline keyboard to provide more options
    keyboard = [
        [InlineKeyboardButton("🏞️ Explore", callback_data='explore_again')],
        [InlineKeyboardButton("🔙 Go Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response_message, parse_mode='Markdown', reply_markup=reply_markup)

