import random
from shared import get_player, update_player
from telegram import Update
from telegram.ext import *

# Function to generate interactive inventory display
async def get_inventory_display(inventory):
    if not inventory or inventory.strip() == "Empty":
        return "Your inventory is currently empty. Try collecting some resources!"

    items = inventory.split(", ")
    item_icons = {
        "wood": "🌲",
        "stone": "🪨",
        "leaves": "🍂",
        "herbs": "🌿",
        "crafted_weapon": "🗡️"
    }

    # Count each item and create a dictionary of counts
    item_counts = {}
    for item in items:
        item = item.strip()  # Remove extra spaces
        if item:  # Check if the item is not an empty string
            item_counts[item] = item_counts.get(item, 0) + 1

    inventory_display = []
    for item, count in item_counts.items():
        icon = item_icons.get(item, "📦")  # Default to box icon if item not found
        inventory_display.append(f"{icon} {item.capitalize()} (x{count})")

    # Return a formatted string with all items
    return "\n".join(inventory_display) if inventory_display else "Your inventory is currently empty."


# Function to generate a visual health bar
async def get_health_bar(health):
    total_segments = 10  # 10 segments for health (each representing 10 points of health)
    filled_segments = health // 10  # Filled segments based on health
    empty_segments = total_segments - filled_segments

    health_bar = "❤️" * filled_segments + "🖤" * empty_segments  # Hearts for filled and empty segments
    return health_bar

# Function to show the player's reputation in stars or medals
async def get_reputation_visual(reputation):
    total_segments = 5  # 5 stars or medals to represent reputation
    filled_segments = reputation // 20  # Filled based on reputation (100 max)
    empty_segments = total_segments - filled_segments

    reputation_bar = "⭐" * filled_segments + "⚫" * empty_segments  # Stars for reputation level
    return reputation_bar

# Function to display player's current location with icons
async def get_location_icon(location):
    location_icons = {
        "Beach": "🏝️ Beach",
        "Forest": "🌲 Forest",
        "Village": "🏘️ Village",
        "Mountains": "🏔️ Mountains",
        "Temple": "🏛️ Temple",
        "Cave": "🕳️ Cave"
    }
    return location_icons.get(location, "📍 Unknown Location")  # Default to 'Unknown Location'

# Setup Inventory Command
async def inventory(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = await get_player(user_id)  # Assuming get_player is also async

    if player:
        inventory = player[3] if player[3] else "Empty"
        health = player[1]
        reputation = player[2]
        location = player[5]

        # Await the health bar generation
        health_bar = await get_health_bar(health)
        reputation_bar = get_reputation_visual(reputation)
        location_icon = get_location_icon(location)

        # Await the inventory display
        inventory_display = await get_inventory_display(inventory)

        inv_text = (
            f"🧍 **Player Profile** 🧍\n\n"
            f"**Location**: {location_icon}\n"
            f"**Health**: {health} {health_bar}\n"
            f"**Reputation**: {reputation} {reputation_bar}\n"
            f"**Inventory**:\n{inventory_display}\n"
        )
        await update.message.reply_text(inv_text, parse_mode='Markdown')  # Await the reply
    else:
        await update.message.reply_text("You need to start the game with /start first.")
    context.chat_data  # Access chat data to ensure context is used


# Helper function to display inventory, reused in both command and button callbacks
async def show_inventory(user_id, message):
    player = await get_player(user_id)  # Assuming get_player is also async

    if player:
        inventory = player[3] if player[3] else "Empty"
        health = player[1]
        reputation = player[2]
        location = player[5]

        # Get visual health bar
        health_bar = await get_health_bar(health)  # Await the health bar generation
        
        # Get reputation stars or medals
        reputation_bar = get_reputation_visual(reputation)  # Assuming this is still sync

        # Get location icon
        location_icon = get_location_icon(location)  # Assuming this is still sync

        # Get inventory display
        inventory_display = await get_inventory_display(inventory)  # Await the inventory display
        
        inv_text = (
            f"🧍 **Player Profile** 🧍\n\n"
            f"**Location**: {location_icon}\n"
            f"**Health**: {health} {health_bar}\n"
            f"**Reputation**: {reputation} {reputation_bar}\n"
            f"**Inventory**:\n{inventory_display}\n"
        )
        await message.reply_text(inv_text, parse_mode='Markdown')  # Await the reply
    else:
        await message.reply_text("You need to start the game with /start first.")  # Await the reply


# Command: /collect (collect resources)


async def collect_resources(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = await get_player(user_id)  # Await the asynchronous player retrieval

    if player:
        new_resource = random.choice(["wood", "stone", "leaves", "herbs"])
        inventory = player[3] + f", {new_resource}" if player[3] else new_resource
        
        await update_player(user_id, "inventory", inventory)  # Await updating the player's inventory

        # Show the updated inventory display after collecting the resource
        updated_inventory_display = await get_inventory_display(inventory)  # Await inventory display

        # Update player's inventory message
        await update.message.reply_text(  # Await the reply
            f"You collected **{new_resource}**! 🎉\n\n"
            f"Use /inv to check your inventory.\n"
            f"**Updated Inventory**:\n{updated_inventory_display}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("You need to start the game with /start first.")  # Await the reply
    context.chat_data  # Access chat data to ensure context is used


async def check_inventory(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await show_inventory(user_id, update.message)  # Await the helper function

    context.chat_data  # Access chat data to ensure context is used
