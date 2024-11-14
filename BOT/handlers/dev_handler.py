import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.db_utils import get_all_players, delete_player
# from main import app

# List of developer user IDs (for authorization)
DEV_USER_IDS = [5956598856]

def is_dev(user_id):
    """Check if the user ID belongs to a developer."""
    return user_id in DEV_USER_IDS

from BOT.main import app

@app.on_message(filters.command("dev") & filters.private)
async def dev(client: Client, message: Message):
    """Display information about all players."""
    if not is_dev(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    players = get_all_players()
    if not players:
        await message.reply_text("No players found.")
        return

    player_info = "\n".join(
        [f"ID: {player['user_id']}, Health: {player['health']}, Location: {player['location']}" for player in players]
    )
    await message.reply_text(f"Number of players: {len(players)}\n\n{player_info}")
from BOT.main import app

@app.on_message(filters.command("delete_player") & filters.private)
async def delete_player_data(client: Client, message: Message):
    """Delete a specific player's data by user ID."""
    if not is_dev(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply_text("Usage: /delete_player <user_id> (numeric)")
        return

    user_id = int(args[1])
    if delete_player(user_id):
        await message.reply_text(f"Player data for user_id {user_id} has been deleted.")
        logging.info(f"Developer deleted player data for user_id {user_id}.")
    else:
        await message.reply_text(f"No player found with user_id {user_id}.")
        logging.warning(f"Attempted to delete non-existent player with user_id {user_id}.")

app.run()
