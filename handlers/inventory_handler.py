from telegram import Update
from utils.db_utils import load_player
from typing import Optional
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
    await update.message.reply_text(response_message, parse_mode='Markdown')

def get_player_status(player) -> str:
    location = player.location or "Unknown location"
    health = player.health or 100
    max_health = player.max_health or 100
    inventory_list = "\n".join(f"- {item}" for item in player.inventory) if player.inventory else "Your inventory is empty."
    health_bar = "[" + "█" * (health * 10 // max_health) + " " * (10 - (health * 10 // max_health)) + "]"

    return (
        f"📍 *Location:* {location}\n"
        f"❤️ *Health:* {health}/{max_health}\n"
        f"🎒 *Inventory:*\n{inventory_list}\n\n"
        f"🩺 *Health Status:* {health_bar}"
    )
