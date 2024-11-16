from pyrogram import Client, filters
import logging
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from pyrogram.enums import ParseMode
from utils.db_utils import load_player
from utils.decorators import maintenance_mode_only
from utils.shared_utils import get_health_bar, get_stamina_bar, get_inventory_space
import json

with open('/workspaces/island_gamebot/data/resources.json') as f:
    resources = json.load(f)

# Command Handler
@maintenance_mode_only
async def inventory_command_handler(client: Client, message: Message):
    """Command handler to display the inventory."""
    await display_inventory(client, message)

# Function to display inventory
@maintenance_mode_only
async def display_inventory(client: Client, message: Message):
    """Display the player's inventory."""
    user_id = message.from_user.id  # Retrieve the user's ID from the query
    try:
        player = await load_player(user_id)

        if player is None:
            await message.reply("Player not found. Please register first.")
            return

        # Generate health and stamina bars
        health_bar = get_health_bar(player.health, player.max_health)
        stamina_bar = get_stamina_bar(player.stamina, player.max_stamina)
        _, remaining_space, total_space = get_inventory_space(player)
        inventory_list = "\n".join(player.inventory) if player.inventory else "Empty"

        # Build the inventory message
        inventory_message = (
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>  Status of {player.name} </b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>  •HP•</b>\n"
            f"<b>| {health_bar} |</b>\n"
            f"              <b>(|{player.health}/{player.max_health}|)</b>\n"
            f"<b>  •Stamina•</b>\n"
            f"<b>| {stamina_bar} |</b>\n"
            f"                   <b>(|{player.stamina}/{player.max_stamina}|)</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>Inventory:\n -> {inventory_list}</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>📍 Location: {player.location}</b>\n"
            f"<b>🏆 Level: {player.level} | </b><b>XP: (|{player.experience}/{player.max_experience}|)</b>\n"
            f"<b>🛠️ Inv Space: (|{remaining_space}/{total_space}|)</b>\n"
            f"━━━━━━━━━━━━━━━━━\n\n"
        )

        # Send the inventory message
        await message.reply_text(inventory_message, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Error displaying inventory for user {user_id}: {e}")
        await message.reply("An error occurred while displaying the inventory. Please try again later.")


# Register function to integrate in main.py
def register(app: Client):
    app.add_handler(MessageHandler(inventory_command_handler, filters.command("inventory")))