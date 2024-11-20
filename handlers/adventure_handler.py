import random
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.handlers import CallbackQueryHandler
from pyrogram.enums import ParseMode
from utils.db_utils import load_player, save_player
from utils.decorators import maintenance_mode_only
from utils.shared_utils import get_health_bar, get_stamina_bar, get_max_health
from handlers.inventory_handler import inventory_command_handler
from utils.inventory_utils import get_inventory_capacity
import json

# Load the events data from event.json
with open('/workspaces/island_gamebot/data/events.json') as f:
    events = json.load(f)

# Load the items data from items.json
with open('/workspaces/island_gamebot/data/items.json') as f:
    items_data = json.load(f)["items"]

# Load the dev config for exploration
with open('/workspaces/island_gamebot/data/config.json') as f:
    config = json.load(f)


# Handle player death and restart the game
async def handle_player_death(player, message):
    player.stamina = config["max_stamina"]["base"] + (player.level * config["max_stamina"]["per_level"])  # Restore stamina
    player.inventory.clear()  # Clear inventory
    await save_player(player)
    await message.reply(
        f"{player.name} has died.\n"
        "💔 You lost all your items, but your health and stamina have been restored.\n"
        "Explore carefully next time!"
    )

@Client.on_message(filters.command("explore") & filters.private)
@maintenance_mode_only
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

    if not player.started_adventure:
        player.started_adventure = True
        await save_player(player)
        logging.info(f"Player {player.name} has started a new adventure.")

    # Determine the current location based on the player's exploration progress
    if player.exploration_progress < 10:
        current_location = "Beach"
    elif player.exploration_progress < 20:
        current_location = "Mountain"
    elif player.exploration_progress < 30:
        current_location = "Caves"
    elif player.exploration_progress < 40:
        current_location = "Dark Forest"
    else:
        current_location = "Desert"

    # Calculate max health and stamina based on the current level
    player.max_health = config["max_health"]["base"] + (player.level * config["max_health"]["per_level"])
    player.max_stamina = config["max_stamina"]["base"] + (player.level * config["max_stamina"]["per_level"])

    # Get inventory capacity based on the current location
    inventory_capacity = get_inventory_capacity(player, current_location, config, items_data)
    # Check if player has enough capacity for new items
    if len(player.inventory) < inventory_capacity:
        # Proceed with item collection and exploration logic
        event_message, resources_collected, xp_gained, item_message = handle_exploration_event(player, current_location)
    else:
        await message.reply("Your inventory is full. You need to make space before you can explore further.")
        return

    # Deduct stamina based on config
    stamina_deduction = random.randint(config["stamina_usage"]["min"], config["stamina_usage"]["max"])
    player.stamina -= stamina_deduction

    # Ensure stamina does not go below 0
    if player.stamina < 0:
        player.stamina = 0

    # Handle health deduction if stamina is at 0
    if player.stamina == 0:
        health_deduction = random.randint(5, 12)
        player.health -= health_deduction

    # Ensure health does not drop below 0
    if player.health <= 0:
        await handle_player_death(player, message)
        return

    # Add XP gained from exploration
    player.experience += xp_gained

    # Level-up logic
    if player.experience >= player.level * config["level_requirements"]["xp_per_level"]:
        player.level += 1
        player.experience = 0
        logging.info(f"Player {player.name} leveled up to level {player.level}")

    # Save player data after all updates
    await save_player(player)

    try:
        # Reply with exploration message
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Show Inventory", callback_data="show_inventory")]])

        health_bar = get_health_bar(player.health, player.max_health)
        stamina_bar = get_stamina_bar(player.stamina, player.max_stamina)

        response_message = f"<b>•HP•</b>\n" \
                           f"<b>| {health_bar} |</b>\n" \
                           f"              <b>(|{player.health}/{player.max_health}|)</b>\n" \
                           f"<b>•Stamina•</b>\n" \
                           f"<b>| {stamina_bar} |</b>\n" \
                           f"                   <b>(|{player.stamina}/{player.max_stamina}|)</b>\n\n" \
                           f"<b>You explored the {current_location}</b>\n" \
                           f"<b>Items found:</b>\n" \
                           f"{item_message}\n\n" \
                           f"<b>Total XP gained: {xp_gained} ✨</b>\n\n" \
                           f"{event_message}"

        await message.reply(response_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

    except Exception as e:
        logging.error(f"An error occurred during exploration: {e}")
        await message.reply("An error occurred. Please try again later.")

# Handle exploration event
def handle_exploration_event(player, current_location):
    resources_collected = []
    encounter_message = ""
    total_xp_gain = 0
    item_message = ""

    # Filter items based on the current location
    location_items = [item for item in items_data if item["location"].lower() == current_location.lower()]

    # Check if there are any items in the location
    if not location_items:
        logging.warning(f"No items found in {current_location}.")
        item_message = "None"
    else:
        # Pick a random number of items (between 1 to 4 items, with a higher chance of picking 4)
        num_items_to_collect = random.choices([1, 2, 3, 4], weights=[0.1, 0.2, 0.3, 0.4])[0]

        # Collect random items from the available location items
        collected_items = random.sample(location_items, k=min(num_items_to_collect, len(location_items)))

        if not collected_items:
            logging.warning(f"No items collected in {current_location}.")
            item_message = "None"
        else:
            resources_collected = collected_items  # Final collected items
            item_message = "\n".join(f"{item['name']}" for item in resources_collected)

    # Choose a random event message if available
    if current_location in events:
        encounter_message = random.choice(events[current_location])

    # Add items to inventory and calculate XP
    item_counts = {}
    for resource in resources_collected:
        item_name = resource["name"]
        if len(player.inventory) < get_inventory_capacity(player, current_location, config, items_data):  # Check if there is space in inventory
            player.inventory.append(resource)  # Add item to inventory
            item_counts[item_name] = item_counts.get(item_name, 0) + 1

            # Calculate XP based on type
            xp_per_item = config["xp_gain"]["per_item"]
            total_xp_gain += xp_per_item  # Add XP for the item

    # Apply level multiplier
    total_xp_gain *= config["xp_gain"]["level_multiplier"]

    # Create item message
    item_message_parts = []
    for item_name, count in item_counts.items():
        item_message_parts.append(f"{item_name} (x{count})")
    item_message = "\n".join(item_message_parts) if item_message_parts else "None"

    # Choose a random event message if available
    if current_location in events:
        encounter_message = random.choice(events[current_location])

    return encounter_message, resources_collected, total_xp_gain, item_message


# Check inventory function
async def check_inventory(client: Client, query: CallbackQuery):
    await query.answer()

    try:
        if query.data == "show_inventory":
            await inventory_command_handler(query)

    except Exception as e:
        logging.error(f"An error occurred in check_inventory: {e}")
        await query.message.reply(
            "An error occurred while checking your inventory. Please try again later."
        )

# Register function for explore command in main.py
def register(app: Client):
    app.on_message(filters.command("explore") & maintenance_mode_only)(explore)
    app.add_handler(CallbackQueryHandler(check_inventory))
