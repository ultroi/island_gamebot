import logging
from collections import Counter
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.enums import ParseMode
from utils.db_utils import load_player, save_player
from utils.shared_utils import get_health_bar, get_stamina_bar
from utils.inventory_utils import get_inventory_capacity
from handlers.error_handler import send_error_to_owner
import json
from typing import Dict
import traceback

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
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    with open(items_config_path, 'r') as items_config_file:
        items_config = json.load(items_config_file)

    total_capacity = get_inventory_capacity(player, player.location, config, items_config)
    used_space = sum(config["space_per_item"].get(item.get("type", "common"), 0) for item in player.inventory)
    remaining_space = total_capacity - used_space

    return {"used": used_space, "remaining": remaining_space, "capacity": total_capacity}


# Command handler to display inventory
async def inventory_command_handler(client: Client, message: Message):
    user_id = message.from_user.id
    await display_inventory(client, message)


# Function to display the inventory
async def display_inventory(client: Client, message: Message):
    try:
        if message.from_user.is_bot:
            bot_username = (await client.get_me()).username
            logging.info(f"Bot {bot_username} is triggering the explore function. Skipping.")
            return

        user_id = message.from_user.id
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
            [[InlineKeyboardButton(" Bag ", callback_data='show_items')]]
        )

        await message.reply(inventory_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    except Exception as e:
        # Log the error and send notification to the owner
        error_message = "".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        )
        logger.error(f"Error during back to inventory: {error_message}", exc_info=True)
        await send_error_to_owner(client, error_message)


# Register handlers
def register(app: Client):
    app.add_handler(MessageHandler(inventory_command_handler, filters.command("inv")))
    
