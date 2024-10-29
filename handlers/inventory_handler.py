# handlers/inventory_handler.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.db_utils import load_player

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    player = load_player(user_id)
    if not player:
        await update.message.reply_text("You need to start your adventure first using /start.")
        return

    # Show player's current location
    location = player.location if player.location else "Unknown location"
    
    # Show player's health
    health = player.health if player.health else 100
    
    # Show player's inventory
    inventory_list = "\n".join(f"- {item}" for item in player.inventory) if player.inventory else "Your inventory is empty."
    
    # Visual representation of health
    health_bar = "❤️" * (health // 10) + "🖤" * (10 - (health // 10))
    
    response_message = (
        f"📍 *Location:* {location}\n"
        f"❤️ *Health:* {health}\n"
        f"🎒 *Inventory:*\n{inventory_list}\n\n"
        f"🩺 *Health Status:* {health_bar}"
    )
    
    await update.message.reply_text(response_message, parse_mode='Markdown')