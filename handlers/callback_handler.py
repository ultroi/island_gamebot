from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import CallbackQueryHandler
from utils.db_utils import load_player, save_player
from utils.shared_utils import get_inventory_capacity, get_health_bar, get_stamina_bar
from utils.inventory_utils import get_item_details
from handlers.inventory_handler import inventory_command_handler
import json
import logging

# Load config and items data
with open('/workspaces/island_gamebot/data/config.json') as f:
    config = json.load(f)

with open('/workspaces/island_gamebot/data/items.json') as f:
    items_data = json.load(f)["items"]

# Check inventory function (moved from adventure_handler)
@Client.on_callback_query(filters.regex("check_inventory"))
async def check_inventory(client: Client, callback_query: CallbackQuery):
    await callback_query.answer()

    try:
        if callback_query.data == "show_inventory":
            await inventory_command_handler(client, callback_query.message)

    except Exception as e:
        logging.error(f"An error occurred in check_inventory: {e}")
        await callback_query.message.reply(
            "An error occurred while checking your inventory. Please try again later."
        )

# Handler for inventory interaction
@Client.on_callback_query(filters.regex("show_inventory"))
async def show_inventory(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    player = await load_player(user_id)
    
    if player is None:
        await callback_query.answer("Player data could not be loaded. Please try again later.", show_alert=True)
        return

    # Get the player's inventory and check capacity
    inventory = player.inventory
    inventory_capacity = get_inventory_capacity(player, player.current_location, config, items_data)
    
    if not inventory:
        await callback_query.answer("Your inventory is empty.", show_alert=True)
        return
    
    item_details = []
    for item in inventory:
        item_details.append(get_item_details(item))
    
    inventory_message = "\n".join(item_details) if item_details else "No items found."
    inventory_message += f"\n\nCapacity: {len(inventory)} / {inventory_capacity}"

    await callback_query.message.edit_text(
        f"<b>Your Inventory:</b>\n\n{inventory_message}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_inventory")]])
    )


# Handler for managing item usage or inventory closure
@Client.on_callback_query(filters.regex("use_item_"))
async def use_item(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    player = await load_player(user_id)
    
    if player is None:
        await callback_query.answer("Player data could not be loaded. Please try again later.", show_alert=True)
        return

    item_name = callback_query.data.split("_", 2)[-1]
    item = next((item for item in player.inventory if item["name"] == item_name), None)
    
    if not item:
        await callback_query.answer(f"Item {item_name} not found in your inventory.", show_alert=True)
        return

    # Apply item effect
    if "health" in item:
        player.health += item["health"]
        if player.health > player.max_health:
            player.health = player.max_health
        await callback_query.answer(f"Used {item_name}. Restored {item['health']} health.")
    elif "stamina" in item:
        player.stamina += item["stamina"]
        if player.stamina > player.max_stamina:
            player.stamina = player.max_stamina
        await callback_query.answer(f"Used {item_name}. Restored {item['stamina']} stamina.")
    elif "mana" in item:
        player.mana += item["mana"]
        await callback_query.answer(f"Used {item_name}. Restored {item['mana']} mana.")
    
    # Remove item from inventory
    player.inventory.remove(item)
    await save_player(client, player)
    
    await callback_query.message.edit_text(
        f"Used item: {item_name}\n\nUpdated Stats:\n" 
        f"Health: {player.health}/{player.max_health}\n"
        f"Stamina: {player.stamina}/{player.max_stamina}\n"
        f"Mana: {player.mana}/{player.max_mana}\n\n"
        "Your inventory has been updated.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_inventory")]])
    )


# Close the inventory view
@Client.on_callback_query(filters.regex("close_inventory"))
async def close_inventory(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()


# Handler for showing player's stats (health, stamina, etc.)
@Client.on_callback_query(filters.regex("show_stats"))
async def show_stats(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    player = await load_player(user_id)
    
    if player is None:
        await callback_query.answer("Player data could not be loaded. Please try again later.", show_alert=True)
        return

    health_bar = get_health_bar(player.health, player.max_health)
    stamina_bar = get_stamina_bar(player.stamina, player.max_stamina)

    stats_message = f"<b>•HP•</b>\n" \
                    f"<b>| {health_bar} |</b>\n" \
                    f"    <b>(|{player.health}/{player.max_health}|)</b>\n" \
                    f"<b>•Stamina•</b>\n" \
                    f"<b>| {stamina_bar} |</b>\n" \
                    f"    <b>(|{player.stamina}/{player.max_stamina}|)</b>\n" \
                    f"\nLevel: {player.level}\nXP: {player.experience}/{player.level * config['level_requirements']['xp_per_level']}\n"

    await callback_query.message.edit_text(
        f"<b>Your Stats:</b>\n\n{stats_message}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Close", callback_data="close_inventory")]])
    )


# Function to register the handlers
def register(app: Client):
    app.add_handler(CallbackQueryHandler(check_inventory))
    app.add_handler(CallbackQueryHandler(show_inventory, filters.regex("show_inventory")))
    app.add_handler(CallbackQueryHandler(use_item, filters.regex("use_item_")))
    app.add_handler(CallbackQueryHandler(close_inventory, filters.regex("close_inventory")))
    app.add_handler(CallbackQueryHandler(show_stats, filters.regex("show_stats")))
    

