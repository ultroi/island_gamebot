import random
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize bot with your credentials
app = Client("survival_bot", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

# Connect to SQLite database
conn = sqlite3.connect('survival_game.db')
cursor = conn.cursor()

# Database Setup
def setup_db():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        health INTEGER,
        reputation INTEGER,
        inventory TEXT,
        resources TEXT,
        location TEXT,
        story_progress TEXT
    )
    ''')
    conn.commit()

# Create new player profile
def create_player(user_id):
    cursor.execute('''
    INSERT INTO players (user_id, health, reputation, inventory, resources, location, story_progress)
    VALUES (?, 100, 0, ?, ?, ?, ?)
    ''', (user_id, '', '', 'Beach', ''))
    conn.commit()

# Get player data
def get_player(user_id):
    cursor.execute('SELECT * FROM players WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

# Update player data
def update_player(user_id, field, value):
    cursor.execute(f'UPDATE players SET {field} = ? WHERE user_id = ?', (value, user_id))
    conn.commit()

# Command: /start
@app.on_message(filters.command("start"))
def start(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if not player:
        create_player(user_id)
        welcome_text = (
            "🌴 **Welcome to Island Survival Adventure!** 🌴\n\n"
            "You are stranded on a mysterious island. Your goal is to survive, explore, and uncover the island's secrets.\n"
            "Tap **'Let's Begin'** to start your adventure!"
        )
        buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Let's Begin", callback_data="begin_explore")]])
        message.reply_text(welcome_text, reply_markup=buttons)
    else:
        message.reply_text("You have already started your adventure. Use /explore to continue.")

# Command: /explore
@app.on_message(filters.command("explore"))
def explore(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        events = [
            "You found a hidden cave with strange markings.",
            "You encountered a wild bear!",
            "You found an abandoned tribal village.",
            "You discovered an old temple with mystical powers.",
            "A peddler offers you supplies in exchange for resources."
        ]
        event = random.choice(events)
        
        response_text = f"🌍 **Exploration Event** 🌍\n\n{event}\n\nWhat will you do next?"
        explore_buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Collect Resources", callback_data="collect_resources"),
             InlineKeyboardButton("Move On", callback_data="move_on")],
            [InlineKeyboardButton("Check Inventory", callback_data="check_inventory")]
        ])
        message.reply_text(response_text, reply_markup=explore_buttons)
    else:
        message.reply_text("You need to start the game with /start first.")

# Function to generate a visual health bar
def get_health_bar(health):
    total_segments = 10  # 10 segments for health (each representing 10 points of health)
    filled_segments = health // 10  # Filled segments based on health
    empty_segments = total_segments - filled_segments

    health_bar = "❤️" * filled_segments + "🖤" * empty_segments  # Hearts for filled and empty segments
    return health_bar

# Function to show the player's reputation in stars or medals
def get_reputation_visual(reputation):
    total_segments = 5  # 5 stars or medals to represent reputation
    filled_segments = reputation // 20  # Filled based on reputation (100 max)
    empty_segments = total_segments - filled_segments

    reputation_bar = "⭐" * filled_segments + "⚫" * empty_segments  # Stars for reputation level
    return reputation_bar

# Function to display player's current location with icons
def get_location_icon(location):
    location_icons = {
        "Beach": "🏝️ Beach",
        "Forest": "🌲 Forest",
        "Village": "🏘️ Village",
        "Mountains": "🏔️ Mountains",
        "Temple": "🏛️ Temple",
        "Cave": "🕳️ Cave"
    }
    return location_icons.get(location, "📍 Unknown Location")  # Default to 'Unknown Location'

# Function to generate interactive inventory display
def get_inventory_display(inventory):
    if not inventory:
        return "Empty"
    
    items = inventory.split(", ")
    item_icons = {
        "wood": "🌲",
        "stone": "🪨",
        "leaves": "🍂",
        "herbs": "🌿",
        "crafted_weapon": "🗡️"
    }

    # Count each item in inventory
    item_counts = {item: items.count(item) for item in set(items)}
    
    # Display each item with its count and icon
    inventory_display = []
    for item, count in item_counts.items():
        icon = item_icons.get(item, "📦")  # Default to a box if no icon found
        inventory_display.append(f"{icon} {item.capitalize()} (x{count})")
    
    return "\n".join(inventory_display)

# Command: /inv (inventory)
@app.on_message(filters.command("inv"))
def inventory(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        inventory = player[3] if player[3] else "Empty"
        health = player[1]
        reputation = player[2]
        location = player[5]

        # Get visual health bar
        health_bar = get_health_bar(health)
        
        # Get reputation stars or medals
        reputation_bar = get_reputation_visual(reputation)

        # Get location icon
        location_icon = get_location_icon(location)

        # Get inventory display
        inventory_display = get_inventory_display(inventory)
        
        inv_text = (
            f"🧍 **Player Profile** 🧍\n\n"
            f"**Location**: {location_icon}\n"
            f"**Health**: {health} {health_bar}\n"
            f"**Reputation**: {reputation} {reputation_bar}\n"
            f"**Inventory**:\n{inventory_display}\n"
        )
        message.reply_text(inv_text)
    else:
        message.reply_text("You need to start the game with /start first.")

# Command: /collect (collect resources)
@app.on_callback_query(filters.regex("collect_resources"))
def collect_resources(client, callback_query):
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    if player:
        new_resource = random.choice(["wood", "stone", "leaves", "herbs"])
        inventory = player[3] + f", {new_resource}" if player[3] else new_resource
        update_player(user_id, "inventory", inventory)
        
        callback_query.message.edit_text(f"You collected {new_resource}!\n\nUse /inv to check your inventory.")

# Command: /craft
@app.on_message(filters.command("craft"))
def craft(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        resources = player[4].split(", ") if player[4] else []
        if "wood" in resources and "stone" in resources:
            update_player(user_id, "resources", "")
            update_player(user_id, "inventory", player[3] + ", crafted_weapon")
            message.reply_text("You crafted a stone weapon!")
        else:
            message.reply_text("You don't have enough resources to craft anything.")


# Function to check available resources for building quality tiers and compare with required materials
def get_building_quality(inventory):
    items = inventory.split(", ") if inventory else []
    
    # Count items in inventory
    item_counts = {item: items.count(item) for item in set(items)}
    wood = item_counts.get("wood", 0)
    leaves = item_counts.get("leaves", 0)
    stones = item_counts.get("stone", 0)

    # Required materials for each quality
    requirements = {
        "Low Grade": {"wood": 3},
        "+ Grade": {"wood": 3, "leaves": 2},
        "++ Grade": {"wood": 3, "stones": 2},
        "+++ Grade": {"wood": 3, "stones": 2, "leaves": 2}
    }

    # Check which grade can be built and how many materials are still needed
    possible_grades = {}
    
    for grade, req in requirements.items():
        missing = {item: req[item] - item_counts.get(item, 0) for item in req}
        if all(v <= 0 for v in missing.values()):  # If no missing materials
            possible_grades[grade] = {"status": "Can build", "missing": {}}
        else:
            possible_grades[grade] = {"status": "Missing materials", "missing": missing}

    return possible_grades, item_counts  # Return possible shelter grades and current inventory count

# Command: /build (build shelter)
@app.on_message(filters.command("build"))
def build(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        inventory = player[3]
        # Determine the building quality based on available materials
        possible_grades, item_counts = get_building_quality(inventory)

        build_message = "🏠 **Build Shelter** 🏠\n\n"
        build_options = []

        # Show each possible shelter grade and required/missing materials
        for grade, status_info in possible_grades.items():
            status = status_info['status']
            missing_text = ""
            if status == "Missing materials":
                missing_text = " (Need more: " + ", ".join(
                    f"{item} ({abs(count)} more)" for item, count in status_info['missing'].items()
                ) + ")"
            
            build_message += f"{grade}: {status}{missing_text}\n"
            
            # If buildable, add to interactive options
            if status == "Can build":
                build_options.append([InlineKeyboardButton(f"Build {grade}", callback_data=f"build_{grade.replace(' ', '_').lower()}")])

        # Check if there are any build options available
        if build_options:
            message.reply_text(
                build_message + "\nChoose the shelter quality to build:",
                reply_markup=InlineKeyboardMarkup(build_options)
            )
        else:
            message.reply_text(build_message + "\nYou don't have enough materials to build any shelter.")
    else:
        message.reply_text("You need to start the game with /start first.")

# Callback to handle building shelters
@app.on_callback_query(filters.regex(r"build_(.+)"))
def handle_build_shelter(client, callback_query):
    quality = callback_query.data.split("_")[1].replace("_", " ")
    user_id = callback_query.from_user.id
    player = get_player(user_id)

    # Deduct materials based on the building quality
    if quality == "low_grade":
        update_inventory(user_id, "wood", remove=True, count=3)
    elif quality == "grade_wood_leaves":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "leaves", remove=True, count=2)
    elif quality == "grade_wood_stones":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "stone", remove=True, count=2)
    elif quality == "grade_wood_stones_leaves":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "stone", remove=True, count=2)
        update_inventory(user_id, "leaves", remove=True, count=2)

    callback_query.message.edit_text(f"You have successfully built a **{quality.replace('_', ' ')}** shelter!")

# Helper function to update inventory (with the ability to remove multiple items)
def update_inventory(user_id, item, remove=False, count=1):
    player = get_player(user_id)
    items = player[3].split(", ") if player[3] else []

    if remove:
        for _ in range(count):
            if item in items:
                items.remove(item)
    else:
        items.extend([item] * count)

    # Update the player's inventory in the database
    new_inventory = ", ".join(items)
    update_player(user_id, "inventory", new_inventory)


# Function to check if the player has built a shelter in the current location
def has_shelter_in_location(player):
    current_location = player[5]  # Player's current location
    shelter_status = player[6]    # Player's shelter status (story_progress could be used for this)
    
    return f"shelter_{current_location}" in shelter_status

# Command: /use_shelter (use the shelter if available in the current location)
@app.on_message(filters.command("use_shelter"))
def use_shelter(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        current_location = player[5]  # This tracks the current location
        shelter_status = player[6]    # This tracks whether a shelter was built in the current location

        if has_shelter_in_location(player):
            shelter_type = shelter_status.split("_")[1]  # Extract shelter quality based on the current location
            benefits = shelter_benefits(shelter_type)

            if benefits:
                # Regenerate health based on shelter quality
                health_regen = benefits["health_regen"]
                current_health = player[1]
                new_health = min(current_health + health_regen, 100)  # Cap health at 100

                update_player(user_id, "health", new_health)

                message.reply_text(
                    f"🏠 **Using Shelter in {current_location}** 🏠\n\n"
                    f"You rested in your **{shelter_type.replace('_', ' ')}** shelter.\n"
                    f"🌿 **Health Regeneration**: +{health_regen}\n"
                    f"🛡️ **Protection**: {benefits['protection']}\n"
                    f"Your current health is now: {new_health}/100."
                )
            else:
                message.reply_text("You don't have a shelter to use.")
        else:
            message.reply_text(f"You haven't built a shelter in the **{current_location}**. Use /build to construct one.")
    else:
        message.reply_text("You need to start the game with /start first.")

# Command: /build (build shelter in the current location)
@app.on_message(filters.command("build"))
def build(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        inventory = player[3]
        current_location = player[5]
        # Determine the building quality based on available materials
        possible_grades, item_counts = get_building_quality(inventory)

        build_message = f"🏠 **Build Shelter in {current_location}** 🏠\n\n"
        build_options = []

        # Show possible shelter grades and required/missing materials
        for grade, status_info in possible_grades.items():
            status = status_info['status']
            missing_text = ""
            if status == "Missing materials":
                missing_text = " (Need more: " + ", ".join(
                    f"{item} ({abs(count)} more)" for item, count in status_info['missing'].items()
                ) + ")"
            
            build_message += f"{grade}: {status}{missing_text}\n"

            # If buildable, add to interactive options
            if status == "Can build":
                build_options.append([InlineKeyboardButton(f"Build {grade}", callback_data=f"build_{grade.replace(' ', '_').lower()}")])

        if build_options:
            message.reply_text(
                build_message + "\nChoose the shelter quality to build:",
                reply_markup=InlineKeyboardMarkup(build_options)
            )
        else:
            message.reply_text(build_message + "\nYou don't have enough materials to build any shelter.")
    else:
        message.reply_text("You need to start the game with /start first.")

# Update shelter build to track the current location where it was built
@app.on_callback_query(filters.regex(r"build_(.+)"))
def handle_build_shelter(client, callback_query):
    quality = callback_query.data.split("_")[1].replace("_", " ")
    user_id = callback_query.from_user.id
    player = get_player(user_id)
    current_location = player[5]

    # Store the built shelter in the current location
    update_player(user_id, "story_progress", f"shelter_{current_location}_{quality.replace(' ', '_').lower()}")

    # Deduct materials based on the shelter quality
    if quality == "low_grade":
        update_inventory(user_id, "wood", remove=True, count=3)
    elif quality == "grade_wood_leaves":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "leaves", remove=True, count=2)
    elif quality == "grade_wood_stones":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "stone", remove=True, count=2)
    elif quality == "grade_wood_stones_leaves":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "stone", remove=True, count=2)
        update_inventory(user_id, "leaves", remove=True, count=2)

    callback_query.message.edit_text(f"You have successfully built a **{quality.replace('_', ' ')}** shelter in **{current_location}**!")

# Command: /move (move to a new location)
@app.on_message(filters.command("move"))
def move(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    # Available locations to move to (could be dynamic based on player progress)
    locations = ["Beach", "Forest", "Mountains", "Village"]

    move_message = "🌍 **Choose your next location** 🌍\n\nWhere would you like to go?"
    location_buttons = [
        [InlineKeyboardButton(location, callback_data=f"move_{location.lower()}")] for location in locations
    ]
    
    message.reply_text(move_message, reply_markup=InlineKeyboardMarkup(location_buttons))

@app.on_callback_query(filters.regex(r"move_(.+)"))
def handle_move_location(client, callback_query):
    new_location = callback_query.data.split("_")[1].capitalize()
    user_id = callback_query.from_user.id

    # Update the player's location to the new location
    update_player(user_id, "location", new_location)

    callback_query.message.edit_text(f"You have moved to the **{new_location}**.\nYou need to build a new shelter here if you want to rest.")

# Shelter levels and required resources
SHELTER_LEVELS = {
    1: {"wood": 15, "leaves": 0, "stones": 0},  # Only wood
    2: {"wood": 15, "leaves": 10, "stones": 0},  # Wood + Leaves
    3: {"wood": 20, "leaves": 0, "stones": 15},  # Wood + Stones
    4: {"wood": 15, "leaves": 10, "stones": 20}  # Wood + Stones + Leaves
}

# Helper function to check if player has enough resources for a shelter level
def can_craft_shelter(user_id, shelter_level):
    player = get_player(user_id)
    inventory = player[3].split(", ") if player[3] else []

    # Count the player's resources
    wood = inventory.count("wood")
    leaves = inventory.count("leaves")
    stones = inventory.count("stones")

    # Get required materials for the shelter level
    required = SHELTER_LEVELS[shelter_level]
    
    # Check if the player has enough materials
    if wood >= required["wood"] and leaves >= required["leaves"] and stones >= required["stones"]:
        return True
    else:
        return False

# Function to deduct the materials from the player's inventory after crafting
def deduct_resources(user_id, shelter_level):
    player = get_player(user_id)
    inventory = player[3].split(", ") if player[3] else []

    # Deduct the required resources
    required = SHELTER_LEVELS[shelter_level]
    
    for _ in range(required["wood"]):
        inventory.remove("wood")
    for _ in range(required["leaves"]):
        inventory.remove("leaves")
    for _ in range(required["stones"]):
        inventory.remove("stones")
    
    # Update the player's inventory
    update_inventory(user_id, ", ".join(inventory))

# Command: /build (build or upgrade shelter)
@app.on_message(filters.command("build"))
def build_shelter(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        inventory = player[3]
        current_location = player[5]

        # Shelter options for the player to choose
        buttons = [
            [InlineKeyboardButton("Level 1 Shelter (Wood)", callback_data="build_shelter_1")],
            [InlineKeyboardButton("Level 2 Shelter (Wood + Leaves)", callback_data="build_shelter_2")],
            [InlineKeyboardButton("Level 3 Shelter (Wood + Stones)", callback_data="build_shelter_3")],
            [InlineKeyboardButton("Level 4 Shelter (Wood + Stones + Leaves)", callback_data="build_shelter_4")]
        ]
        
        message.reply_text(
            "🏠 **Build Shelter** 🏠\n\n"
            "Choose the shelter level you want to build or upgrade to, based on your resources:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

# Callback for shelter building
@app.on_callback_query(filters.regex(r"build_shelter_(\d)"))
def handle_build_shelter(client, callback_query):
    shelter_level = int(callback_query.data.split("_")[2])
    user_id = callback_query.from_user.id
    
    if can_craft_shelter(user_id, shelter_level):
        # Deduct resources and confirm shelter build
        deduct_resources(user_id, shelter_level)
        
        # Update the shelter status in the player's data
        update_player(user_id, "story_progress", f"shelter_level_{shelter_level}")
        
        callback_query.message.edit_text(
            f"🏠 You have successfully built a **Level {shelter_level} Shelter**!\n"
            "You can now save the game and rest here."
        )
    else:
        # If the player doesn't have enough resources
        callback_query.message.edit_text(
            f"❌ You don't have enough resources to build a **Level {shelter_level} Shelter**.\n"
            "Check your inventory and try again."
        )




# Initialize the database and start the bot
setup_db()
app.run()
