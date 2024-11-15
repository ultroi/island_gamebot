import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.db_utils import get_all_players, delete_player
from typing import List

# List of developer user IDs (for authorization)
DEV_USER_IDS = [5956598856]

# Developer authorization decorator
def dev_only(func):
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if message.from_user.id not in DEV_USER_IDS:
            await message.reply_text("You are not authorized to use this command.")
            logging.warning(f"Unauthorized access attempt by user {message.from_user.id}.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

# Display information about all players
@Client.on_message(filters.command("dev") & filters.private)
@dev_only
async def dev(client: Client, message: Message):
    """Display information about all players."""
    players = get_all_players()
    if not players:
        await message.reply_text("No players found.")
        return

    player_info = "\n".join(
        [f"ID: {player['user_id']}, Health: {player['health']}, Location: {player['location']}" for player in players]
    )
    await message.reply_text(f"Number of players: {len(players)}\n\n{player_info}")
    logging.info("Developer accessed player information.")

# Delete a specific player's data by user ID
@Client.on_message(filters.command("delete_player") & filters.private)
@dev_only
async def delete_player_data(client: Client, message: Message):
    """Delete a specific player's data by user ID."""
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply_text("Usage: /delete_player <user_id> (numeric)")
        logging.error("Invalid /delete_player command usage.")
        return

    user_id = int(args[1])
    if delete_player(user_id):
        await message.reply_text(f"Player data for user_id {user_id} has been deleted.")
        logging.info(f"Developer deleted player data for user_id {user_id}.")
    else:
        await message.reply_text(f"No player found with user_id {user_id}.")
        logging.warning(f"Attempted to delete non-existent player with user_id {user_id}.")

# Register function to add handlers in main.py
def register(app: Client):
    app.on_message(filters.command("dev") & filters.private)(dev)
    app.on_message(filters.command("delete_player") & filters.private)(delete_player_data)
