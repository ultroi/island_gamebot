# handlers/help_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.text_responses import HELP_MESSAGE

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_MESSAGE)