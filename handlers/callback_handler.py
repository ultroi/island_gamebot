from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.handlers import CallbackQueryHandler
from handlers.start_handler import show_game_brief, start_solo_arc, show_narrative_placeholder 
from handlers.adventure_handler import explore
from utils.db_utils import load_player, save_player
from utils.shared_utils import get_health_bar, get_stamina_bar
from handlers.inventory_handler import get_inventory_capacity
from handlers.error_handler import error_handler_decorator
import logging
import json
from models.player import Player  # Adjust the import path as necessary

# Load config and items data
with open('/workspaces/island_gamebot/data/config.json') as f:
    config = json.load(f)

with open('/workspaces/island_gamebot/data/items.json') as f:
    items_data = json.load(f)["items"]

#-----------------------------------------------------------------------------------#
@error_handler_decorator
async def start_adventure(_, message: Message):
    """Handles the 'Start Adventure' button click."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    logging.info(f"User {user_name} ({user_id}) started a new adventure.")

    # Show game brief with options to start Solo or Story Adventure
    await show_game_brief(message)

@error_handler_decorator
async def start_solo_arc(client: Client, query: CallbackQuery):
    """Starts a Solo Expedition adventure."""
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    player = Player(user_id=user_id, name=user_name, arc_type='solo', started_adventure=True)
    await save_player(player)

    await query.message.edit_text("🧭 Starting Solo Expedition! Let’s see how you fare on your own.")
    await explore(client, query.message)  # Replace 'explore' with solo adventure logic

@error_handler_decorator
async def show_narrative_placeholder(query: CallbackQuery):
    """Starts the Narrative Adventure (story-driven)."""
    await query.message.edit_text(
        "📖 <b>Narrative Arc Coming Soon!</b>\n\n"
        "Get ready for a unique, story-driven adventure where your choices shape the journey.",
        parse_mode=ParseMode.HTML
    )
#-----------------------------------------------------------------------------------#

# Inventory Management
@error_handler_decorator
async def check_inventory(client: Client, query: CallbackQuery):
    """Handler for checking inventory."""
    try:
        user_id = query.from_user.id
        player = await load_player(user_id)
        
        if not player:
            await query.answer("Player data not found. Please try again later.", show_alert=True)
            return
        
        inventory = player.inventory
        inventory_capacity = get_inventory_capacity(player, player.current_location, config, items_data)

        if not inventory:
            await query.answer("Your inventory is empty.", show_alert=True)
            return
        
        inventory_list = "\n".join(f"{item['name']} (x{item['quantity']})" for item in inventory)
        inventory_message = (
            f"<b>Your Inventory:</b>\n\n{inventory_list}\n\n"
            f"Capacity: {len(inventory)} / {inventory_capacity}"
        )

        await query.message.edit_text(
            inventory_message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_inventory")]]))
    except Exception as e:
        logging.error(f"Error in check_inventory: {e}")
        await query.message.reply("An error occurred while checking your inventory. Please try again later.")

# Use Item
@error_handler_decorator
async def use_item(client: Client, query: CallbackQuery):
    """Handler for using items."""
    try:
        user_id = query.from_user.id
        player = await load_player(user_id)

        if not player:
            await query.answer("Player data not found. Please try again later.", show_alert=True)
            return

        item_name = query.data.split("_", 2)[-1]
        item = next((i for i in player.inventory if i["name"] == item_name), None)

        if not item:
            await query.answer(f"Item {item_name} not found in inventory.", show_alert=True)
            return

        # Apply item effects
        if "health" in item:
            player.health = min(player.max_health, player.health + item["health"])
            message = f"Used {item_name}. Restored {item['health']} health."
        elif "stamina" in item:
            player.stamina = min(player.max_stamina, player.stamina + item["stamina"])
            message = f"Used {item_name}. Restored {item['stamina']} stamina."
        elif "mana" in item:
            player.mana = min(player.max_mana, player.mana + item["mana"])
            message = f"Used {item_name}. Restored {item['mana']} mana."
        else:
            message = f"Used {item_name}."

        player.inventory.remove(item)
        await save_player(player)
        await query.answer(message)
        await check_inventory(client, query)  # Refresh inventory view
    except Exception as e:
        logging.error(f"Error in use_item: {e}")
        await query.answer("An error occurred. Please try again.", show_alert=True)


# Register Handlers
def register(app: Client):
    app.add_handler(CallbackQueryHandler(start_adventure, filters.regex('^start_adventure$')))
    app.add_handler(CallbackQueryHandler(start_solo_arc, filters.regex('^solo_arc$')))
    app.add_handler(CallbackQueryHandler(show_narrative_placeholder, filters.regex('^narrative_arc$')))
    app.add_handler(CallbackQueryHandler(check_inventory, filters.regex("check_inventory")))
    app.add_handler(CallbackQueryHandler(use_item, filters.regex("use_item_")))
