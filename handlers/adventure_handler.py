import random
import json
import logging
from collections import Counter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_utils import load_player, save_player
from utils.decorators import user_verification, maintenance_mode_only

# Load resources, areas, and events from JSON files
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {file_path}: {e}")
        return {}

resources = load_json_file('/workspaces/island_gamebot/data/resources.json')
areas = load_json_file('/workspaces/island_gamebot/data/areas.json')
events = load_json_file('/workspaces/island_gamebot/data/events.json')

@user_verification
@maintenance_mode_only
async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        await update.message.reply_text("This command can only be used via button interaction.")
        return
    user_id = query.from_user.id

    # Load player data
    player = load_player(user_id)
    if not player:
        message = "You need to start your adventure first using /start."
        await (query.answer(message) if query else update.message.reply_text(message))
        return

    # Exploration outcome setup
    event_message, item_received = handle_exploration_event(player)

    # Health bar display
    health_bar = calculate_health_bar(player.health, player.max_health)
    player_status = f"<b>{player.name}</b>\n{health_bar}\n<b>{player.health}/{player.max_health}</b>"

    # Item received message
    item_message = generate_item_message(item_received)

    try:
        reply_markup = get_inline_keyboard()
        response_message = f"{player_status}\n\n{event_message}{item_message}\n\nWhat would you like to do next?"

        # Send response
        if query:
            await query.message.reply_text(response_message, reply_markup=reply_markup, parse_mode='HTML')
        else:
            await update.message.reply_text(response_message, reply_markup=reply_markup, parse_mode='HTML')

        # Chance for location change
        if random.random() < 0.01:
            new_location = random.choice(list(areas.keys()))
            if new_location != player.location:
                player.location = new_location
                await update.message.reply_text(f"🏞️ You've discovered a new area: <b>{new_location}</b>!", parse_mode='HTML')

        # Save player changes
        save_player(player)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        message = "An error occurred. Please try again later."
        await (query.answer(message) if query else update.message.reply_text(message))

def handle_exploration_event(player):
    event_message, item_received = "", None

    # Main exploration events (19% chance)
    if random.random() < 0.19:
        if not events:
            return "No events available.", None
        event = random.choice(events)
        event_message = f"🔍 **Exploration Event**\n*{event['description']}*"
        outcomes = event["outcomes"]

        if "gain_health" in outcomes:
            player.health = min(player.health + outcomes["gain_health"], player.max_health)
            event_message += "\n✨ You feel rejuvenated and regain some health!"
        if "lose_health" in outcomes:
            player.health = max(player.health - outcomes["lose_health"], 0)
            event_message += "\n⚠️ A challenging encounter left you a bit wounded."

        if "gain_item" in outcomes:
            gained_items = outcomes["gain_item"]
            if isinstance(gained_items, list):
                for item in gained_items:
                    player.inventory.append(item)
                    event_message += f"\n🎁 You found a **{item}**!"
            else:
                player.inventory.append(gained_items)
                event_message += f"\n🎁 You found a **{gained_items}**!"
    else:
        if random.random() < 0.8:
            location_items = resources.get(player.location, [])
            if location_items:
                random_item = random.choice(location_items)
                player.inventory.append(random_item)
                item_received = random_item
                event_message = f"🌟 You found something useful: **{random_item}**!"
            else:
                event_message = "You search around, but find nothing this time."
        else:
            no_item_messages = [
                "You search around, but find nothing this time.",
                "It seems the area has little to offer right now.",
                "Your exploration yields no discoveries today.",
                "Despite your efforts, you come up empty-handed.",
                "Just empty pockets and empty hands this time."
            ]
            event_message = random.choice(no_item_messages)
    
    return event_message, item_received

def calculate_health_bar(health, max_health, bar_length=15):
    filled_length = int(round(bar_length * health / float(max_health)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    return f"{bar}"

def generate_item_message(item_received):
    if not item_received:
        return ""
    
    item_messages = [
        f"🌟 You found something useful: **{item_received}**!",
        f"✨ Lucky find! You picked up **{item_received}**.",
        f"🔍 Your keen eye spots **{item_received}** among the surroundings.",
        f"💎 Discovery! You've added **{item_received}** to your inventory.",
        f"📦 You stumble upon **{item_received}** and add it to your supplies."
    ]
    return f"\n\n{random.choice(item_messages)}"

def get_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Check Inventory", callback_data='check_inventory')],
        [InlineKeyboardButton("Explore Again", callback_data='explore_again')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_player_status(player) -> str:
    # Header and player info
    name = player.name
    health = player.health or 100
    max_health = player.max_health or 100
    
    # Visual health bar based on player's health
    health_bar_length = 15
    filled_length = int(health_bar_length * health / max_health)
    health_bar = "[" + "█" * filled_length + " " * (health_bar_length - filled_length) + "]"

    # Location and Inventory
    location = player.location or "Mysterious Island"
    item_counts = Counter(player.inventory)
    inventory_list = "\n".join(
        f"🔹 *{item}* x{count}" for item, count in item_counts.items()
    ) if item_counts else "👜 Your inventory is empty."

    # Final message
    return (
        f"🏝️ *Island Adventure Inventory*\n\n"
        f"👤 *Name:* {name}\n"
        f"❤️ *Health:* {health}/{max_health}\n"
        f"{health_bar}\n\n"
        f"📍 *Current Location:* {location}\n\n"
        f"🎒 *Items:* \n{inventory_list}\n\n"
        "Choose your next move below!"
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    callback_data = query.data

    try:
        await query.answer()  # Acknowledge the callback query

        if callback_data == 'check_inventory':
            await check_inventory(update, context)
        elif callback_data == 'explore_again':
            await explore(update, context)
    except Exception as e:
        logging.error(f"An error occurred in callback_handler: {e}")
        await query.message.reply_text("An error occurred. Please try again later.")

async def check_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        await update.message.reply_text("This command can only be used via button interaction.")
        return
    user_id = query.from_user.id

    # Load player data
    player = load_player(user_id)
    if not player:
        await query.answer("You need to start your adventure first using /start.")
        return

    # Get player status
    player_status = get_player_status(player)

    # Send player status
    try:
        await query.message.edit_text(player_status, parse_mode='HTML')
    except Exception as e:
        logging.error(f"An error occurred while updating the message: {e}")
        await query.answer("An error occurred. Please try again later.")
