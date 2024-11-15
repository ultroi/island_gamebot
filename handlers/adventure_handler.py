import random
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from utils.db_utils import load_player, save_player
from utils.decorators import user_verification, maintenance_mode_only
from collections import Counter
from inventory_handler import get_inventory_capacity, calculate_health_bar
from data import resources, areas, events

# Exploration command handler
async def explore(client: Client, message: Message):
    user_id = message.from_user.id
    player = await load_player(user_id)

    # Check if the player has started the adventure
    if not player.started_adventure:
        await message.reply("You need to start your adventure first using /start.")
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
    health_bar = calculate_health_bar(player.health, player.max_health)
    player_status = f"<b>{player.name}</b>\n{health_bar}\n<b>{player.health}/{player.max_health}</b>"
    item_message = generate_item_message(item_received)

    try:
        reply_markup = get_inline_keyboard()
        response_message = f"{player_status}\n\n{event_message}{item_message}"
        await message.reply(response_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

        # 1% chance to discover a new area
        if random.random() < 0.01:
            new_location = random.choice(list(areas.keys()))
            if new_location != player.location:
                player.location = new_location
                await message.reply(f"🏞️ You've discovered a new area: <b>{new_location}</b>!", parse_mode=ParseMode.HTML)
        
        await save_player(player)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await message.reply("An error occurred. Please try again later.")

def handle_exploration_event(player, current_area):
    # Generate random resources and encounters based on the current area
    resources_collected = []
    encounter_message = ""
    
    # Select resources based on current area
    area_resources = resources.get(current_area, [])
    if area_resources:
        resources_collected = random.choices(area_resources, k=3)  # Collect 3 items

    # Handle specific encounters based on area
    if current_area == "Beach":
        encounter_message = random.choice(events["Beach"])
    elif current_area == "Mountain":
        encounter_message = random.choice(events["Mountain"])
    elif current_area == "Caves":
        encounter_message = random.choice(events["Caves"])
    elif current_area == "Dark Forest":
        encounter_message = random.choice(events["Dark Forest"])
    elif current_area == "Desert":
        encounter_message = random.choice(events["Desert"])

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

def get_inline_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Show Inventory", callback_data="show_inventory")]
    ])

# Register function for explore command in main.py
def register(app: Client):
    app.on_message(filters.command("explore") & user_verification & maintenance_mode_only)(explore)
