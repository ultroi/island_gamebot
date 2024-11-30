import random
import logging
import json
import asyncio
from pyrogram.handlers import MessageHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ParseMode
from utils.db_utils import load_player, save_player
from utils.decorators import maintenance_mode_only
from utils.shared_utils import get_health_bar, get_stamina_bar
from handlers.inventory_handler import get_inventory_capacity
from handlers.error_handler import error_handler_decorator

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

### --- Configuration Loader --- ###
def load_json_file(filepath):
    """Load JSON data from the specified file."""
    with open(filepath, "r") as f:
        return json.load(f)

# Load configuration and data files
CONFIG_PATHS = {
    "events": "/workspaces/island_gamebot/data/events.json",
    "items": "/workspaces/island_gamebot/data/items.json",
    "config": "/workspaces/island_gamebot/data/config.json",
}

config = {
    key: load_json_file(path) for key, path in CONFIG_PATHS.items()
}

events = config["events"]
items_data = config["items"]["items"]

### --- Helper Functions --- ###
@error_handler_decorator
async def get_location_based_on_progress(progress, message):
    """Determine the player's current location based on their exploration progress."""
    if progress < 10:
        return "Beach"
    elif progress < 20:
        return "Mountain"
    elif progress < 30:
        return "Caves"
    elif progress < 40:
        return "Dark Forest"
    return "Desert"


@error_handler_decorator
async def filter_items_by_location(location, message):
    """Filter items available in the specified location."""
    return [item for item in items_data if item["location"].lower() == location.lower()]


@error_handler_decorator
async def calculate_exploration_rewards(player, current_location):
    """Determine the rewards (items, XP, encounter message, and effects) for an exploration, including biome effects and endurance penalties."""
    
    # Apply biome effects based on the player's location
    player.apply_biome_effect()
    
    # Apply endurance penalties based on player's stamina and health
    player.apply_endurance_penalties()

    # Get items based on current location
    location_items = await filter_items_by_location(current_location, None)
    if not location_items:
        logger.warning(f"No items found in {current_location}.")
        return "None", [], 0, ""

    # Randomly collect items based on configured probabilities
    num_items_to_collect = random.choices([1, 2, 3, 4], weights=[0.1, 0.2, 0.3, 0.4])[0]
    collected_items = random.sample(location_items, k=min(num_items_to_collect, len(location_items)))

    # Add items to inventory and calculate XP gain
    item_counts = {}
    total_xp_gain = 0
    for item in collected_items:
        if len(player.inventory) < get_inventory_capacity(player, current_location, config["config"], items_data):
            player.inventory.append(item)
            item_counts[item["name"]] = item_counts.get(item["name"], 0) + 1
            # Reduced XP gain to make progression harder
            total_xp_gain += config["config"]["xp_gain"]["per_item"] * 0.75  # Less XP for hardcore

    # Apply XP scaling based on player's level with the new hardcore multiplier
    total_xp_gain *= config["config"]["xp_gain"]["level_multiplier"] * 0.5  # Harder scaling

    # Build item message
    item_message = "\n".join(f"{name} (x{count})" for name, count in item_counts.items()) or "None"

    # Generate encounter message based on the current location and random events
    encounter_message = random.choice(events[current_location]) if current_location in events else ""

    # Include any additional effects (like environmental effects or random events)
    special_effect_message = ""
    if current_location == "Dark Forest":
        special_effect_message = "🌲 The forest feels eerie... something might be watching you..."
    elif current_location == "Mountain":
        special_effect_message = "⛰️ The air is thin, making it harder to breathe... but you're brave!"
    elif random.random() < 0.1:  # 10% chance for a random event effect
        special_effect_message = "⚡ A sudden storm rolls in! You feel the wind howl and the rain pour down!"

    # Combine encounter and special effect messages
    full_encounter_message = f"{encounter_message}\n{special_effect_message}".strip()

    return item_message, collected_items, total_xp_gain, full_encounter_message



@error_handler_decorator
async def update_player_stats(player, stamina_deduction):
    """Update the player's stamina and health after exploration."""
    player.stats["stamina"] = max(0, player.stats["stamina"] - stamina_deduction)
    if player.stats["stamina"] == 0:
        health_deduction = random.randint(5, 12)
        player.stats["health"] = max(0, player.stats["health"] - health_deduction)
    return player

@error_handler_decorator
async def handle_player_death(player, message):
    """Handle the player's death by resetting stats and clearing inventory."""
    player.stamina = config["config"]["max_stamina"]["base"] + (player.level * config["config"]["max_stamina"]["per_level"])
    player.inventory.clear()
    await save_player(player)
    await message.reply(
        f"{player.name} has died.\n"
        "💔 You lost all your items, but your health and stamina have been restored.\n"
        "Explore carefully next time!"
    )

def build_exploration_response(player, current_location, item_message, xp_gained):
    """Construct the response message for the exploration result."""
    health_bar = get_health_bar(player.stats["health"], player.stats["max_health"])
    stamina_bar = get_stamina_bar(player.stats["stamina"], player.stats["max_stamina"])
    return (
        f"<b>•HP•</b>\n<b>| {health_bar} |</b>\n"
        f"              <b>(|{player.stats['health']}/{player.stats['max_health']}|)</b>\n"
        f"<b>•Stamina•</b>\n<b>| {stamina_bar} |</b>\n"
        f"                   <b>(|{player.stats['stamina']}/{player.stats['max_stamina']}|)</b>\n\n"
        f"<b>You explored the {current_location}</b>\n"
        f"<b>Items found:</b>\n{item_message}\n\n"
        f"<b>Total XP gained: {xp_gained} ✨</b>\n"
    )

### --- Command Handlers --- ###
@maintenance_mode_only
@error_handler_decorator
async def explore(client: Client, message: Message):
    user_id = message.from_user.id
    player = await load_player(user_id)

    if not player:
        await message.reply("Player data could not be loaded. Please try again later.")
        return

    if not player.started_adventure:
        player.started_adventure = True
        await save_player(player.user_id, player)

    current_location = await get_location_based_on_progress(player.exploration_progress, message)
    inventory_capacity = get_inventory_capacity(player, current_location, config["config"], items_data)

    if len(player.inventory) >= inventory_capacity:
        await message.reply("Your inventory is full. You need to make space before you can explore further.")
        return

    item_message, _, xp_gained, encounter_message = await calculate_exploration_rewards(player, current_location)
    
    stamina_deduction = random.randint(config["config"]["stamina_usage"]["min"], config["config"]["stamina_usage"]["max"])
    player = await update_player_stats(player, stamina_deduction)

    if player.stats['health'] <= 0:
        await handle_player_death(player, message)
        return

    player.experience += xp_gained
    level_up_xp = player.level * config["config"]["level_requirements"]["xp_per_level"]
    if player.experience >= level_up_xp:
        player.level += 1
        player.experience = 0

    await save_player(player.user_id, player)

    response_message = build_exploration_response(player, current_location, item_message, xp_gained, encounter_message)
    if not response_message.strip():
        logger.error("Response message is empty!")
        await message.reply("An error occurred while generating the response. Please try again later.")
        return

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Show Inventory", callback_data="show_inventory")]])
    await message.reply(response_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


@maintenance_mode_only
@error_handler_decorator
async def rest(client: Client, message: Message):
    user_id = message.from_user.id
    player = await load_player(user_id)

    if not player:
        await message.reply("Player data could not be loaded. Please try again later.")
        return

    # Send an initial loading message
    loading_message = await message.reply("Resting... [▒▒▒▒▒▒▒▒▒▒] 0%")

    # Define progress steps for the animation
    progress_steps = [
        "[█▒▒▒▒▒▒▒▒▒] 10%",
        "[██▒▒▒▒▒▒▒▒] 20%",
        "[███▒▒▒▒▒▒▒] 30%",
        "[████▒▒▒▒▒▒] 40%",
        "[█████▒▒▒▒▒] 50%",
        "[██████▒▒▒▒] 60%",
        "[███████▒▒▒] 70%",
        "[████████▒▒] 80%",
        "[█████████▒] 90%",
        "[██████████] 100%"
    ]

    # Simulate the progress animation
    for step in progress_steps:
        await asyncio.sleep(0.5)  # Adjust speed as necessary
        await loading_message.edit_text(f"Resting... {step}")

    # Final message
    await loading_message.edit_text("Fully rested! 🌟")

    # Restore player's stamina
    player.stats["stamina"] = player.stats["max_stamina"]
    await save_player(player.user_id, player)

    # Send a message indicating that the player's stamina has been restored
    await loading_message.edit_text(
        f"{player.name} has fully rested.\n"
        "✨ Your stamina has been restored to maximum!"
    )


### --- Registration --- ###
def register(app: Client):
    app.add_handler(MessageHandler(explore, filters.command("explore")))
    app.add_handler(MessageHandler(rest, filters.command("rest")))
