import logging
import asyncio
from client import app
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from collections import Counter
from pyrogram.handlers import MessageHandler
from handlers.error_handler import error_handler_decorator
from pyrogram.enums import ParseMode
from utils.db_utils import load_player
from utils.shared_utils import get_health_bar, get_stamina_bar
from utils.inventory_utils import get_inventory_capacity
from handlers.error_handler import send_error
from client import app 
import json   
from typing import Dict
import traceback

BOT_ID = 7882763921

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load configuration and item data once
ITEMS_CONFIG_PATH = '/workspaces/island_gamebot/data/items.json'
CONFIG_PATH = '/workspaces/island_gamebot/data/config.json'

with open(ITEMS_CONFIG_PATH) as f:
    items_data = json.load(f)["items"]

with open(CONFIG_PATH) as f:
    config = json.load(f)

@error_handler_decorator
async def get_inventory_space(player, config, items_config) -> Dict[str, int]:
    total_capacity = get_inventory_capacity(player, player.location, config, items_config)
    used_space = sum(
        config["space_per_item"].get(item.get("type", "common"), 0) for item in player.inventory
    )
    remaining_space = total_capacity - used_space
    return {"used": used_space, "remaining": remaining_space, "capacity": total_capacity}

@error_handler_decorator
async def display_inventory(client: Client, message):
    """
    Display the player's inventory with health, stamina, and other stats.
    If message is a CallbackQuery, it uses callback_query.message instead.
    """
    user_id = message.from_user.id
    try:
        logger.info(f"Displaying inventory for user_id={user_id}")

        # Load player data
        player = await load_player(user_id)
        if not player:
            logger.warning(f"Player data not found for user_id={user_id}")
            await message.reply("Player not found. Please register first.")
            return

        # Health and stamina bars
        health_bar = get_health_bar(player.stats["health"], player.stats["max_health"])
        stamina_bar = get_stamina_bar(player.stats["stamina"], player.stats["max_stamina"])

        # Inventory space
        inventory_space = await get_inventory_space(player, config, items_data)
        used_space = inventory_space["used"]
        total_capacity = inventory_space["capacity"]

        # Maximum experience for the next level
        next_level_experience = player.get_max_experience()

        # Inventory message
        inventory_message = (
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>{player.name}</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>• HP:</b>\n"
            f"{health_bar}\n"
            f"    <b>[{player.stats['health']}/{player.stats['max_health']}]</b>\n"
            f"<b>• Stamina:</b>\n"
            f"{stamina_bar}\n"
            f"    <b>[{player.stats['stamina']}/{player.stats['max_stamina']}]</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"📍 <b>Location:</b> {player.location}\n"
            f"🏆 <b>Level:</b> {player.level} | <b>XP:</b> ({player.experience}/{next_level_experience})\n"
            f"🛠️ <b>Inventory Space:</b> {used_space}/{total_capacity}\n"
            f"━━━━━━━━━━━━━━━━━"
        )

        # Inline button for Bag
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(" Bag ", callback_data="show_inventory")]]
        )

        # Check if it's a CallbackQuery or a Message
        if isinstance(message, CallbackQuery):
            await message.message.reply(inventory_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await message.reply(inventory_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    except Exception as e:
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Error displaying inventory for user {user_id}: {error_message}", exc_info=True)
        if isinstance(message, CallbackQuery):
            await send_error(client, message.message.chat.id, error_message)
        else:
            await send_error(client, message.chat.id, error_message)

@app.on_callback_query(filters.regex("show_inventory"))
async def handle_inventory_button(client: Client, callback_query: CallbackQuery):
    """
    Handle button clicks to display the inventory.
    """
    user_id = callback_query.from_user.id

    # Ignore the callback query if it's from the bot itself
    if user_id == BOT_ID:
        logger.warning("Ignoring callback query from bot itself.")
        return

    try:
        # Load player data
        player = await load_player(user_id)
        if not player:
            logger.warning(f"Player data not found for user_id={user_id}")
            await callback_query.message.reply("Player not found. Please register first.")
            return

        # Group and count inventory items by their names
        item_counts = Counter(item['name'] for item in player.inventory)

        # Format the inventory items with correct counts
        inventory_items = "\n".join([f"{item} - {count}" for item, count in item_counts.items()])

        # Inventory message with items
        inventory_message = (
            f"━━━━━━━━━━━━━━━━━\n"
            f"<b>{player.name}'s Inventory</b>\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"{inventory_items}\n"
            f"━━━━━━━━━━━━━━━━━"
        )

        # Inline button for Back to Inventory
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(" Inv ", callback_data="display_inventory")]]
        )

        # Smoothly edit the existing message with new inventory content
        await callback_query.message.edit_text(inventory_message, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        await callback_query.answer()

    except Exception as e:
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Error handling inventory button for user {user_id}: {error_message}", exc_info=True)
        await send_error(client, callback_query.message.chat.id, error_message)


@app.on_callback_query(filters.regex("display_inventory"))
async def handle_back_to_inventory_button(client: Client, callback_query: CallbackQuery):
    """
    Handle button clicks to go back to the main inventory display.
    """
    try:
        # Show loading message to smooth the transition
        await callback_query.message.edit_text("Loading your inventory... Please wait.", parse_mode=ParseMode.HTML)

        # Smooth transition to the main inventory view
        await display_inventory(client, callback_query)
        # Wait for a short duration before deleting the loading message
        await asyncio.sleep(10)
        await callback_query.message.delete()

    except Exception as e:
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Error handling back to inventory button for user {callback_query.from_user.id}: {error_message}", exc_info=True)
        await send_error(client, callback_query.message.chat.id, error_message)

def register(app: Client):
    app.add_handler(MessageHandler(display_inventory, filters.command("inv")))
