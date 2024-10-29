# handlers/adventure_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.game_logic import generate_event
from inventory_handler import inventory
from utils.db_utils import load_player, save_player
import json
import random

# Load areas and resources data with error handling
try:
    with open('data/areas.json') as f:
        areas = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    areas = {}
    print(f"Error loading areas.json: {e}")

try:
    with open('data/resources.json') as f:
        resources = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    resources = {}
    print(f"Error loading resources.json: {e}")

async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Load player data
    player = load_player(user_id)
    if not player:
        await query.answer("You need to start your adventure first using /start.")
        return

    # Provide player's current status
    player_status = await inventory(update, context)

    # Generate a random exploration event and apply any outcomes to the player
    event = generate_event()
    event_message = f"🔍 **Exploration Event**\n{event.description}"

    # Handle different outcomes
    if "gain_health" in event.outcomes:
        player.health = min(player.health + event.outcomes["gain_health"], player.max_health)
        event_message += "\nYou feel rejuvenated and gain some health!"
    elif "lose_health" in event.outcomes:
        player.health = max(player.health - event.outcomes["lose_health"], 0)
        event_message += "\nYou had a rough encounter and lost some health!"
    elif "gain_item" in event.outcomes:
        item_gained = event.outcomes["gain_item"]
        player.inventory.append(item_gained)
        event_message += f"\nYou found a **{item_gained}** during your exploration!"

    # Give a random item based on the player's current location
    current_location = player.location
    if current_location in resources and resources[current_location]:
        random_item = random.choice(resources[current_location])
        player.inventory.append(random_item)
        event_message += f"\n🔹 You found a **{random_item}** while exploring the {current_location}."

    # Save player state after updates
    save_player(player)

    # Prepare "Explore Again" and "Check Inventory" options
    keyboard = [
        [InlineKeyboardButton("Explore Again", callback_data='explore_again')],
        [InlineKeyboardButton("Check Inventory", callback_data='check_inventory')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send combined message with player's status, event details, and options
    await query.message.reply_text(f"{player_status}\n\n{event_message}\n\nWhat would you like to do next?", reply_markup=reply_markup)

    # Determine if the location changes after exploration
    change_location_chance = 0.01  # Increase the chance for more dynamic location changes
    if random.random() < change_location_chance:
        new_location = random.choice(list(areas.keys()))
        if new_location != current_location:
            player.location = new_location
            await query.message.reply_text(f"🏞️ You have ventured to a new location: **{new_location}**.")
            save_player(player)  # Save state after location change

    # Introduce a random animal encounter
    encounter_chance = 0.15  # 15% chance for animal encounter
    if random.random() < encounter_chance:
        await query.message.reply_text("🐾 A wild animal appears! Prepare for a battle!")
        # Call the fight handler if implemented
        # await fight_handler(update, context)

    # Final save to ensure all changes are stored
    save_player(player)


