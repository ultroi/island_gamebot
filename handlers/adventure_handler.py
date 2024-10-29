import random
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_utils import load_player, save_player
from handlers.inventory_handler import get_player_status
from utils.game_logic import generate_event

# Load resources and areas from JSON files
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return {}

resources = load_json_file('/workspaces/island_gamebot/data/resources.json')
areas = load_json_file('/workspaces/island_gamebot/data/areas.json')

def apply_event_outcomes(player, event):
    event_message = f"🔍 **Exploration Event**\n{event.description}"
    outcomes = event.outcomes

    if "gain_health" in outcomes:
        player.health = min(player.health + outcomes["gain_health"], player.max_health)
        event_message += "\nYou feel rejuvenated and gain some health!"
    elif "lose_health" in outcomes:
        player.health = max(player.health - outcomes["lose_health"], 0)
        event_message += "\nYou had a rough encounter and lost some health!"
    elif "gain_item" in outcomes:
        item_gained = outcomes["gain_item"]
        player.inventory.append(item_gained)
        event_message += f"\nYou found a **{item_gained}** during your exploration!"

    return event_message

def give_random_item(player, current_location):
    if current_location in resources and resources[current_location]:
        random_item = random.choice(resources[current_location])
        player.inventory.append(random_item)
        return f"\n🔹 You found a **{random_item}** while exploring the {current_location}."
    return ""

async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    try:
        # Load player data
        player = load_player(user_id)
        if not player:
            await query.answer("You need to start your adventure first using /start.")
            return

        # Provide player's current status
        player_status = get_player_status(player)

        # Generate a random exploration event and apply any outcomes to the player
        event = generate_event()
        event_message = apply_event_outcomes(player, event)

        # Give a random item based on the player's current location
        event_message += give_random_item(player, player.location)

        # Save player state after updates
        save_player(player)

        # Send combined message with player's status, event details, and options
        keyboard = [
            [InlineKeyboardButton("Explore Again", callback_data='explore_again')],
            [InlineKeyboardButton("Check Inventory", callback_data='check_inventory')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"{player_status}\n\n{event_message}\n\nWhat would you like to do next?", reply_markup=reply_markup
        )

        # Determine if the location changes after exploration
        if random.random() < 0.01:  # 1% chance for location change
            new_location = random.choice(list(areas.keys()))
            if new_location != player.location:
                player.location = new_location
                await query.message.reply_text(f"🏞️ You have ventured to a new location: **{new_location}**.")
                save_player(player)  # Save state after location change

        # Introduce a random animal encounter
        if random.random() < 0.15:  # 15% chance for animal encounter
            await query.message.reply_text("🐾 A wild animal appears! Prepare for a battle!")
            # Call the fight handler if implemented
            # await fight_handler(update, context)

        # Final save to ensure all changes are stored
        save_player(player)
    except Exception as e:
        print(f"An error occurred during exploration: {e}")
        await query.message.reply_text("An error occurred while exploring. Please try again later.")
