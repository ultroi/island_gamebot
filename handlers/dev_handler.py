# handlers/dev_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.db_utils import get_all_players, delete_player

async def dev(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.message.from_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    players = get_all_players()
    if not players:
        await update.message.reply_text("No players found.")
        return

    player_info = "\n".join([f"ID: {player['user_id']}, Health: {player['health']}, Location: {player['location']}" for player in players])
    await update.message.reply_text(f"Number of players: {len(players)}\n\n{player_info}")

async def delete_player_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_dev(update.message.from_user.id):
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /delete_player <user_id>")
        return

    user_id = context.args[0]
    if delete_player(user_id):
        await update.message.reply_text(f"Player data for user_id {user_id} has been deleted.")
    else:
        await update.message.reply_text(f"No player found with user_id {user_id}.")

def is_dev(user_id):
    # Replace with actual developer user IDs
    dev_user_ids = [5956598856]
    return user_id in dev_user_ids