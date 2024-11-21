import logging
from collections import Counter
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors import RPCError
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


@Client.on_raw_update()
async def log_raw_updates(client, update, users, chats):
    logger.debug(f"Raw update received: {update}")

# Function to display the inventory
async def display_inventory(client: Client, message: Message):
    user_id = message.from_user.id
    try:
        logger.info(f"Displaying inventory for user_id={user_id}")

        # Load player data
        player = await load_player(user_id)
        if not player:
            logger.warning("Player data not found")
            await message.reply("Player not found. Please register first.")
            return

        # Generate inventory message
        health_bar = get_health_bar(player.health, player.max_health)
        stamina_bar = get_stamina_bar(player.stamina, player.max_stamina)

        inventory_space = get_inventory_space(player, CONFIG_PATH, ITEMS_CONFIG_PATH)
        used_space = inventory_space["used"]
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
            f"🛠️ <b>Inventory Space:</b> {used_space}/{total_capacity}\n"
            f"━━━━━━━━━━━━━━━━━"
        )

        # Inline button for Bag
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Bag", callback_data=f"show_items:{user_id}")]]
        )
        await message.reply_text(inventory_message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Error displaying inventory: {e}", exc_info=True)
        await message.reply("An error occurred while displaying your inventory.")



# Callback handler to show items
@Client.on_callback_query(filters.regex(r"^show_items:\d+$"))
async def show_items_callback(client: Client, callback_query: CallbackQuery):
    try:
        # Log the received callback data
        logger.debug(f"Callback triggered: data={callback_query.data}")

        # Extract user ID from callback data
        user_id = int(callback_query.data.split(":")[1])
        logger.info(f"Processing callback for user_id={user_id}")

        # Acknowledge the callback (important)
        await callback_query.answer("Processing your request...")

        # Load player data
        player = await load_player(user_id)
        if not player:
            logger.warning(f"No player found for user_id={user_id}")
            await callback_query.answer("Player not found. Please register first.", show_alert=True)
            return

        # Generate inventory content
        inventory_counts = Counter(item['name'] for item in player.inventory)
        inventory_list = "\n".join(f"<b>{item}:</b> {count}" for item, count in inventory_counts.items()) or "Empty"

        # Message to display
        items_message = f"━━━━━━━━━━━━━━━━━\n<b>Bag:</b>\n{inventory_list}\n━━━━━━━━━━━━━━━━━"

        # Edit the message or reply inline
        if callback_query.message:
            logger.debug("Editing message for callback")
            await callback_query.message.edit_text(items_message, parse_mode=ParseMode.HTML)
        elif callback_query.inline_message_id:
            logger.debug("Editing inline message for callback")
            await client.edit_inline_text(callback_query.inline_message_id, text=items_message, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Error handling callback: {e}", exc_info=True)
        await callback_query.answer("An error occurred while processing your request.", show_alert=True)

# Register handlers
def register(app: Client):
    app.add_handler(MessageHandler(inventory_command_handler, filters.command("inv")))
    app.add_handler(CallbackQueryHandler(show_items_callback, filters.regex("^show_items$")))