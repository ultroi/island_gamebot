from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from utils.db_utils import load_player
from collections import Counter
from typing import Optional
from utils.decorators import user_verification, maintenance_mode_only


@Client.on_message(filters.command("inventory") & user_verification & maintenance_mode_only)
async def inventory(client: Client, message: Message):
    user_id = message.from_user.id
    player = load_player(user_id)
    
    if not player:
        await message.reply_text("You need to start your adventure first using /start.")
        return

    await show_inventory(client, message, player)


async def show_inventory(client: Client, message: Message, player) -> None:
    response_message = get_player_status(player)
    
    # Creating inline keyboard to provide more options
    keyboard = [
        [InlineKeyboardButton("🏞️ Explore", callback_data='explore_again')],
        [InlineKeyboardButton("🔙 Go Back", callback_data='back_to_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(response_message, parse_mode='markdown', reply_markup=reply_markup)


def get_player_status(player) -> str:
    # Header and player info
    name = player.name
    health = player.health or 100
    max_health = player.max_health or 100
    
    # Visual health bar based on player's health
    health_bar_length = 15
    filled_length = int(health_bar_length * health / max_health)
    health_bar = "[" + "█" * filled_length + " " * (health_bar_length - filled_length) + "]"

    # Location and Inventory
    location = player.location or "Mysterious Island"
    item_counts = Counter(player.inventory)
    inventory_list = "\n".join(
        f"🔹 *{item}* x{count}" for item, count in item_counts.items()
    ) if item_counts else "👜 Your inventory is empty."

    # Final message
    return (
        f"🏝️ *Island Adventure Inventory*\n\n"
        f"👤 *Name:* {name}\n"
        f"❤️ *Health:* {health}/{max_health}\n"
        f"{health_bar}\n\n"
        f"📍 *Current Location:* {location}\n\n"
        f"🎒 *Items:* \n{inventory_list}\n\n"
        "Choose your next move below!"
    )