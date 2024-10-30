import random
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.db_utils import load_player, save_player
from utils.decorators import user_verification, maintenance_mode_only
from handlers.inventory_handler import get_player_status

# Load resources, areas, and events from JSON files
def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return {}

resources = load_json_file('/workspaces/island_gamebot/data/resources.json')
areas = load_json_file('/workspaces/island_gamebot/data/areas.json')
events = load_json_file('/workspaces/island_gamebot/data/events.json')

@user_verification
@maintenance_mode_only
def apply_event_outcomes(player, event):
    event_message = f"🔍 **Exploration Event**\n*{event['description']}*"
    outcomes = event["outcomes"]

    if "gain_health" in outcomes:
        player.health = min(player.health + outcomes["gain_health"], player.max_health)
        event_message += "\n✨ You feel rejuvenated and regain some health!"
    elif "lose_health" in outcomes:
        player.health = max(player.health - outcomes["lose_health"], 0)
        event_message += "\n⚠️ A challenging encounter left you a bit wounded."

    # Handling gain_item as a list
    if "gain_item" in outcomes:
        items = outcomes["gain_item"]
        if isinstance(items, list):
            for item in items:
                player.inventory.append(item)
                event_message += f"\n🎁 You stumbled upon a **{item}**!"
        else:
            player.inventory.append(items)
            event_message += f"\n🎁 You found a **{items}**!"

    return event_message

@user_verification
@maintenance_mode_only
async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        user_id = query.from_user.id
    else:
        user_id = update.message.from_user.id

    # Load player data
    player = load_player(user_id)
    if not player:
        await (query.answer("You need to start your adventure first using /start.") if query
               else update.message.reply_text("You need to start your adventure first using /start."))
        return

    # Reduced chance of main exploration events (5%)
    if random.random() < 0.05:  # 5% chance
        event = events
        event_message = apply_event_outcomes(player, event)
    else:
        # Higher chance for random item discovery (80% chance)
        if random.random() < 0.8:
            random_item = random.choice(list(resources.keys()))
            player.inventory.append(random_item)
            item_received = random_item
            
        # Visual health bar with filled and depleted sections
            health_bar_length = 20
            filled_length = int(health_bar_length * player.health / player.max_health)
            depleted_length = health_bar_length - filled_length


        # Health bar design with █ for filled and ▒ for depleted
        health_bar = '█' * filled_length + '▒' * depleted_length

    # Player status message with right-aligned name, health bar, and health values below
        player_status = (
             f"<b>{player.name:>40}</b>\n"    # Right-aligned name
             f"[{health_bar}]\n"              # Health bar only
                     f"<b>{player.health}/{player.max_health}</b>".rjust(80)  # Right-aligned health values
                     )

    # Item received message
    if item_received:
        item_message = f"\n\nItem Received: **{item_received}**"
    else:
        item_message = ""

    # Send combined message with player's status, event details, and options
    keyboard = [
        [InlineKeyboardButton("🌍 Explore Again", callback_data='explore_again')],
        [InlineKeyboardButton("🎒 Check Inventory", callback_data='check_inventory')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"{player_status}\n\n{event_message}{item_message}\n\nWhat would you like to do next?", reply_markup=reply_markup, parse_mode='HTML'
    )

    # Chance for location change after exploration
    if random.random() < 0.01:  # 1% chance for location change
        new_location = random.choice(list(areas.keys()))
        if new_location != player.location:
            player.location = new_location
            await query.message.reply_text(f"🏞️ You've discovered a new area: <b>{new_location}</b>!", parse_mode='HTML')
            save_player(player)  # Save state after location change

    # Save player changes to ensure all updates are stored
    save_player(player)

