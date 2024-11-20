import logging
from collections import Counter
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from utils.db_utils import load_player, save_player
from utils.shared_utils import get_health_bar, get_stamina_bar
from utils.inventory_utils import get_inventory_capacity
import json
from typing import Dict

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load configuration and item data
ITEMS_CONFIG_PATH = '/workspaces/island_gamebot/data/items.json'
CONFIG_PATH = '/workspaces/island_gamebot/data/config.json'

with open(ITEMS_CONFIG_PATH) as f:
    items_data = json.load(f)["items"]

with open(CONFIG_PATH) as f:
    config = json.load(f)


def get_inventory_space(player, config_path: str, items_config_path: str) -> Dict[str, int]:
    """
    Calculate the used, remaining, and total inventory space for a player.
    """
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    with open(items_config_path, 'r') as items_config_file:
        items_config = json.load(items_config_file)

    total_capacity = get_inventory_capacity(player, player.location, config, items_config)
    used_space = sum(config["space_per_item"].get(item.get("type", "common")) for item in player.inventory)
    remaining_space = total_capacity - used_space

    return {"used": used_space, "remaining": remaining_space, "capacity": total_capacity}


# Function to update player's inventory
async def update_inventory(player, new_items, client: Client, message: Message):
    """
    Update the player's inventory with new items found during exploration.
    """
    try:
        player.inventory.extend(new_items)
        player.stamina = min(player.stamina, player.max_stamina)
        await save_player(player)
        await display_inventory(client, message)

    except Exception as e:
        logger.error(f"Error updating inventory for player {player.id}: {e}", exc_info=True)
        await message.reply("An error occurred while updating inventory. Please try again later.")


# Command handler to display inventory
async def inventory_command_handler(client: Client, message: Message):
    await display_inventory(client, message)


# Function to display the inventory
async def display_inventory(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        player = await load_player(user_id)

        if not player:
            await message.reply("Player not found. Please register first.")
            return

        health_bar = get_health_bar(player.health, player.max_health)
        stamina_bar = get_stamina_bar(player.stamina, player.max_stamina)

        inventory_space = get_inventory_space(player, CONFIG_PATH, ITEMS_CONFIG_PATH)
        remaining_space = inventory_space["remaining"]
        total_capacity = inventory_space["capacity"]
        next_level_experience = player.max_experience

        inventory_message = (
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>{player.name}</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>• HP:</b>\n"
            f"{health_bar}\n"
            f"    <b>[{player.health}/{player.max_health}]</b>\n"
            f"<b>• Stamina:</b>\n"
            f"{stamina_bar}\n"
            f"    <b>[{player.stamina}/{player.max_stamina}]</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>Location:</b> {player.location}\n"
            f"🏆 <b>Level:</b> {player.level} | <b>XP:</b> ({player.experience}/{next_level_experience})\n"
            f"🛠️ <b>Inventory Space:</b> {remaining_space}/{total_capacity}\n"
            f"━━━━━━━━━━━━━━━━━"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Bag", callback_data=f"show_items:{message.from_user.id}")]
            ]
        )

        await message.reply_text(inventory_message, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    
    except Exception as e:
        logger.error(f"Error displaying inventory: {e}", exc_info=True)
        await message.reply("Error occurred while displaying inventory.")
     


# Callback handler to show items
@Client.on_callback_query(filters.regex(r"show_items:\d+"))
async def show_items_callback(client: Client, callback_query: CallbackQuery):
    try:
        # Extract user ID from callback data
        user_id = int(callback_query.data.split(":")[1])
        logger.debug(f"Callback triggered by user ID: {user_id}")

        # Load the player's data
        player = await load_player(user_id)

        # Check if the player exists
        if not player:
            await callback_query.answer("Player not found. Please register first using /start.", show_alert=True)
            return

        # Count items in the player's inventory
        inventory_counts = Counter(item['name'] for item in player.inventory)
        inventory_list = "\n".join(f"<b>{item}:</b> {count}" for item, count in inventory_counts.items()) or "Empty"

        # Create the inventory message
        items_message = (
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>Bag:</b>\n{inventory_list}\n"
            f"━━━━━━━━━━━━━━━━━"
        )

        # Edit the message with the inventory contents
        await callback_query.message.edit_text(items_message, parse_mode=ParseMode.HTML)

        # Acknowledge the button press
        await callback_query.answer("Bag opened!")

    except Exception as e:
        logger.error(f"Error showing items for user {user_id}: {e}", exc_info=True)
        await callback_query.answer("An error occurred while showing your items.", show_alert=True)


# Register handlers
def register(app: Client):
    app.add_handler(MessageHandler(inventory_command_handler, filters.command("inv")))
    app.add_handler(CallbackQueryHandler(show_items_callback, filters.regex("show_items")))
