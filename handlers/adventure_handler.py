import random
import logging
from pyrogram import Client, filters
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.enums import ParseMode
from utils.db_utils import load_player, save_player
from utils.decorators import maintenance_mode_only
from utils.shared_utils import get_inventory_capacity, get_health_bar
import json
from handlers.inventory_handler import display_inventory

with open('/workspaces/island_gamebot/data/resources.json') as f:
    resources = json.load(f)

with open('/workspaces/island_gamebot/data/areas.json') as f:
    areas = json.load(f)

with open('/workspaces/island_gamebot/data/events.json') as f:
    events = json.load(f)

# Exploration command handler
async def explore(client: Client, message: Message):
    if message.from_user.is_bot:
        bot_username = (await client.get_me()).username
        logging.info(f"Bot {bot_username} is triggering the explore function. Skipping.")
        return

    logging.info(f"Exploration command received from user {message.from_user.id} - {message.from_user.first_name}")
    user_id = message.from_user.id
    player = await load_player(user_id)
    
    if player is None:
        await message.reply("Player data could not be loaded. Please try again later.")
        return
    
    # If this is the player's first time exploring, mark it as an adventure started
    if not player.started_adventure:
        player.started_adventure = True
        await save_player(player)  # Save this change
        logging.info(f"Player {player.name} has started a new adventure.")
        return

    # Determine accessible area based on player's level
    if player.level <= 10:
        current_area = "Beach"
    elif player.level <= 20:
        current_area = "Mountain"
    elif player.level <= 30:
        current_area = "Caves"
    elif player.level <= 40:
        current_area = "Dark Forest"
    else:
        current_area = "Desert"

    # Generate exploration event and messages
    event_message, item_received = handle_exploration_event(player, current_area)
    health_bar = get_health_bar(player.health, player.max_health)
    player_status = f"<b>{player.name}</b>\n{health_bar}\n<b>{player.health}/{player.max_health}</b>"
    item_message = generate_item_message(item_received)

    try:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Show Inventory", callback_data="show_inventory")]
        ])
        response_message = f"{player_status}\n\n{event_message}{item_message}"
        await message.reply(response_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        
        await save_player(player)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await message.reply("An error occurred. Please try again later.")


def handle_exploration_event(player, current_area):
    # Generate random resources and encounters based on the current area
    resources_collected = []
    encounter_message = ""

    if current_area in resources:
        area_resources = resources[current_area]
        food_items = area_resources.get("food_item", {})
        non_food_items = area_resources.get("non_fooditem", {})

        # Collect up to 3 items, prioritizing rare items if available
        collected_items = []
        if "rare" in food_items:
            collected_items.extend(random.choices(food_items["rare"], k=min(1, len(food_items["rare"])), weights=[0.2] * len(food_items["rare"])))
        if "common" in food_items:
            collected_items.extend(random.choices(food_items["common"], k=min(2, len(food_items["common"])), weights=[0.8] * len(food_items["common"])))
        if "rare" in non_food_items:
            collected_items.extend(random.choices(non_food_items["rare"], k=min(1, len(non_food_items["rare"])), weights=[0.2] * len(non_food_items["rare"])))
        if "common" in non_food_items:
            collected_items.extend(random.choices(non_food_items["common"], k=min(2, len(non_food_items["common"])), weights=[0.8] * len(non_food_items["common"])))
        
        resources_collected = collected_items[:3]  # Ensure only up to 3 items are collected

    # Handle specific encounters based on area
    if current_area in events:
        encounter_message = random.choice(events[current_area])

    # Add resources to player's inventory
    for resource in resources_collected:
        if len(player.inventory) < get_inventory_capacity(player.level):
            player.inventory.append(resource)
        else:
            encounter_message += "\nYour inventory is full. You couldn't collect all resources."

    # Generate event message
    event_message = f"You explored the {current_area} and found: {', '.join(resources_collected)}.\n{encounter_message}"
    return event_message, resources_collected

def generate_item_message(items):
    if not items:
        return ""
    return f"\n\nYou received: {', '.join(items)}."

async def handle_show_inventory(client: Client, query: CallbackQuery):
    if query.from_user.is_bot:  # Skip if the user is a bot
        return

    logging.info(f"Show Inventory button clicked by user {query.from_user.id} - {query.from_user.first_name}")
    try:
        user_id = query.from_user.id
        player = await load_player(user_id)
        
        if player is None:
            await query.message.reply("Player data could not be loaded. Please try again later.")
            return

        await display_inventory(client, query.message)
    except Exception as e:
        logging.error(f"An error occurred while handling show_inventory: {e}")
        # Send informative message to user
        await query.message.reply(f"An error occurred: {str(e)[:100]}. Please try again later.")

# Register function for explore command in main.py
def register(app: Client):
    app.on_message(filters.command("explore") & maintenance_mode_only)(explore)
    app.add_handler(CallbackQueryHandler(handle_show_inventory, filters.regex("show_inventory")))