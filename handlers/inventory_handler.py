from pyrogram import Client, filters
import math
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode
from utils.db_utils import load_player
from collections import Counter
from utils.decorators import user_verification, maintenance_mode_only
from handlers.adventure_handler import explore  # Import explore handler for future interaction

# Inventory command handler
@Client.on_message(filters.command("inventory") & user_verification & maintenance_mode_only)
async def inventory(client: Client, message: Message):
    user_id = message.from_user.id
    player = await load_player(user_id)
    
    if not player:
        await message.reply_text("You need to start your adventure first using /start.")
        return

    await show_inventory(client, message, player)

# Show inventory for the player
async def show_inventory(client: Client, message: Message, player) -> None:
    response_message = get_player_status(player)
    reply_markup = get_inventory_keyboard()  # Generate inline keyboard
    
    await message.reply_text(response_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

from collections import Counter

def get_inventory_capacity(level, player_inventory, area):
    # Base inventory capacity based on level
    if level <= 10:
        base_capacity = 10
    elif level <= 20:
        base_capacity = 15
    elif level <= 30:
        base_capacity = 20
    elif level <= 40:
        base_capacity = 25
    else:
        base_capacity = 30

    # Adjust capacity based on the area the player is exploring
    if area in ["Beach", "Forest"]:
        base_capacity += 2  # Easier areas, more room for exploration items
    elif area in ["Mountain", "Desert"]:
        base_capacity -= 3  # Harder areas, less room due to higher demands for tools, food, and water
    elif area == "Caves":
        base_capacity -= 2  # Caves might have precious materials but reduced inventory space due to danger
    
    # Calculate the number of items in the current inventory
    current_item_count = len(player_inventory)

    # Calculate the item counts (how many of each item)
    item_counts = Counter(player_inventory)

    # Adjust the capacity based on how full the inventory is
    for item, count in item_counts.items():
        if count > 3:  # If a player is carrying a lot of one item, reduce overall capacity
            base_capacity -= (count - 3)  # Remove extra space for overstocked items
        elif count == 1:  # If only 1 item is present, add space for it
            base_capacity += 1

    # If the player has heavy equipment (like weapons or tools), reduce capacity
    for item in player_inventory:
        if item in ["Iron Sword", "Axe", "Pickaxe"]:  # Example of items that take up more space
            base_capacity -= 2  # These items should take more space in the inventory

    # Ensure the capacity never goes below a minimum of 5 (survival-critical space)
    base_capacity = max(base_capacity, 5)

    # Ensure the inventory capacity does not exceed a maximum limit (50 for highest level)
    return min(base_capacity, 50)

    
def get_health_bar(player):
    health_ratio = player.health / player.max_health
    total_blocks = 10  # Length of health bar (total blocks)
    filled_blocks = math.floor(health_ratio * total_blocks)
    
    health_bar = "█" * filled_blocks + "▒" * (total_blocks - filled_blocks)
    return health_bar

def get_stamina_bar(player):
    stamina_ratio = player.stamina / player.max_stamina
    total_blocks = 10  # Length of stamina bar (total blocks)
    filled_blocks = math.floor(stamina_ratio * total_blocks)
    
    # Full stamina bar with positive (yellow) and negative (gray) sections
    stamina_bar = "🟡" * filled_blocks + "⚪" * (total_blocks - filled_blocks)
    return stamina_bar

# Generate the player's status message
def get_player_status(player):
    health_bar = get_health_bar(player)
    stamina_bar = get_stamina_bar(player)

    # Inventory item counts
    item_counts = Counter(player.inventory)
    inventory_list = "\n".join(
        f"🔹 *{item}* x{count}" for item, count in item_counts.items()
    ) if item_counts else "👜 Your inventory is empty."

    # Status message with interactive health and stamina
    return (
        f"🏝️ **Island Adventure - Player Status**\n\n"
        f"👤 **Name**: {player.name}\n"
        f"❤️ **HP**: {player.health}/{player.max_health}\n"
        f"🔹 **Health Bar**: {health_bar}\n\n"
        f"⚡ **Stamina**: {player.stamina}/{player.max_stamina}\n"
        f"🔹 **Stamina Bar**: {stamina_bar}\n\n"
        f"📍 **Current Location**: {player.location}\n\n"
        f"📦 **Inventory**:\n{inventory_list}\n\n"
        f"🏆 **Level**: {player.level}\n"
        f"💎 **XP**: {player.current_xp}/{player.total_xp}\n"
    )


# Generate inline keyboard for inventory options
def get_inventory_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🏞️ Explore", callback_data='explore_again')],
        [InlineKeyboardButton("🔙 Go Back", callback_data='back_to_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Register function to allow integration in main.py
def register(app: Client):
    app.add_handler(Client.on_message(filters.command("inventory") & user_verification & maintenance_mode_only)(inventory))
