import random
import json
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from utils.db_utils import load_player, save_player
from utils.decorators import user_verification, maintenance_mode_only
from handlers.inventory_handler import show_inventory  # Import the show_inventory function

# Load JSON data for resources, areas, and events
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

# Exploration logic
@user_verification
@maintenance_mode_only
async def explore(client: Client, message):
    user_id = message.from_user.id
    player = load_player(user_id)
    if not player:
        await message.reply("You need to start your adventure first using /start.")
        return

    event_message, item_received = handle_exploration_event(player)
    health_bar = calculate_health_bar(player.health, player.max_health)
    player_status = f"<b>{player.name}</b>\n{health_bar}\n<b>{player.health}/{player.max_health}</b>"
    item_message = generate_item_message(item_received)
    
    try:
        reply_markup = get_inline_keyboard()
        response_message = f"{player_status}\n\n{event_message}{item_message}"
        await message.reply(response_message, reply_markup=reply_markup, parse_mode='html')

        # 1% chance to discover a new area
        if random.random() < 0.01:
            new_location = random.choice(list(areas.keys()))
            if new_location != player.location:
                player.location = new_location
                await message.reply(f"🏞️ You've discovered a new area: <b>{new_location}</b>!", parse_mode='html')
        
        await save_player(player)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await message.reply("An error occurred. Please try again later.")

# Event handler
def handle_exploration_event(player):
    event_message, item_received = "", None
    if random.random() < 0.19:  # 19% chance of event
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

# Health bar generator
def calculate_health_bar(health, max_health, bar_length=15):
    filled_length = int(round(bar_length * health / float(max_health)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    return f"{bar}"

# Generate item message
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

# Inline keyboard
def get_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("Bag", callback_data='check_inventory')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Callback query handler
async def handle_callback_query(client: Client, callback_query: CallbackQuery):
    callback_data = callback_query.data
    await callback_query.answer()  # Acknowledge callback query

    if callback_data == 'check_inventory':
        await callback_query.message.edit("Checking Inventory...")
        await check_inventory(client, callback_query)

# Check inventory function
async def check_inventory(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    player = load_player(user_id)
    if not player:
        await callback_query.answer("You need to start your adventure first using /start.")
        return
    player_status = show_inventory(player)
    await callback_query.message.reply(player_status, parse_mode='markdown')