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

# Command: /inv (inventory)
@app.on_message(filters.command("inv"))
def inventory(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        inventory = player[3] if player[3] else "Empty"
        health = player[1]
        reputation = player[2]
        
        inv_text = (
            f"🧍 **Player Profile** 🧍\n\n"
            f"**Health**: {health}\n"
            f"**Reputation**: {reputation}\n"
            f"**Inventory**: {inventory}\n"
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

# Command: /build (build shelter)
@app.on_message(filters.command("build"))
def build(client, message):
    user_id = message.from_user.id
    player = get_player(user_id)

    if player:
        resources = player[4].split(", ") if player[4] else []
        if "wood" in resources and "leaves" in resources:
            update_player(user_id, "resources", "")
            message.reply_text("You built a wood and leaves shelter!")
        else:
            message.reply_text("You don't have enough resources to build anything.")

# Initialize the database and start the bot
setup_db()
app.run()
