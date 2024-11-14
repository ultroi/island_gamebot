# handlers/help_handler.py
from pyrogram import Client, filters
from utils.text_responses import HELP_MESSAGE

@Client.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(HELP_MESSAGE)