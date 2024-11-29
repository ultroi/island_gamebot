import json
import logging
from functools import wraps
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from datetime import datetime
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Paths to JSON files
CONFIG_FILE = "/workspaces/island_gamebot/data/config.json"
ITEM_FILE = "/workspaces/island_gamebot/data/items.json"
EXPLORATION_FILE = "/workspaces/island_gamebot/data/exploration.json"

# Helper function to load JSON files
def load_json(file_path: str) -> dict:
    """Load JSON data from a file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading {file_path} at {datetime.now()}: {e}")
        return {}

# Helper function to save JSON files
def save_json(file_path: str, data: dict):
    """Save JSON data to a file."""
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        logging.info(f"Configuration saved to {file_path} at {datetime.now()}.")
    except Exception as e:
        logging.error(f"Error saving {file_path} at {datetime.now()}: {e}")

# Developer authorization decorator
DEV_USER_IDS = [5956598856]  # Example developer user IDs

def dev_only(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if message.from_user.id not in DEV_USER_IDS:
            await message.reply_text("🚫 <b>You are not authorized to use this command.</b>", parse_mode=ParseMode.HTML)
            logging.warning(f"Unauthorized access attempt by user {message.from_user.id} at {datetime.now()}.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

# Validate numeric input
def is_valid_numeric_input(args: list, count: int) -> bool:
    """Check if the input arguments are valid numbers."""
    if len(args) != count:
        return False
    return all(arg.isdigit() for arg in args)


# Mock functions for demonstration purposes
async def get_all_players():
    return []

async def delete_player(user_id: int) -> bool:
    return True

# Command: /dev - Display player information
@dev_only
async def dev(client: Client, message: Message):
    """Display information about all players."""
    players = await get_all_players()
    if not players:
        await message.reply_text("📭 <b>No players found.</b>", parse_mode=ParseMode.HTML)
        return

    player_info = "\n".join(
        [f"• <b>Name</b>: {player.name}, <b>ID</b>: <code>{player.user_id}</code>" for player in players]
    )
    await message.reply_text(f"📊 <b>Number of players:</b> {len(players)}\n\n{player_info}", parse_mode=ParseMode.HTML)
    logging.info(f"Developer {message.from_user.id} accessed player information at {datetime.now()}.")

# Command: /delete_player <user_id> - Delete a specific player's data
@dev_only
async def delete_player_data(client: Client, message: Message):
    """Delete a specific player's data by user ID."""
    args = message.text.split()
    if not is_valid_numeric_input(args, 2):
        await message.reply_text("❌ <b>Usage:</b> /delete_player <user_id> *(numeric)*", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    user_id = int(args[1])
    success = await delete_player(user_id)
    if success:
        await message.reply_text(f"✅ <b>Player data for user_id <code>{user_id}</code> has been deleted.</b>", parse_mode=ParseMode.HTML)
        logging.info(f"Developer {message.from_user.id} deleted player data for user_id {user_id} at {datetime.now()}.")
    else:
        await message.reply_text(f"⚠️ <b>No player found with user_id <code>{user_id}</code>.</b>", parse_mode=ParseMode.HTML)
        logging.warning(f"Attempted to delete non-existent player with user_id {user_id} at {datetime.now()}.")

# Check if input values are valid numbers
def is_valid_numeric_input(args, expected_length):
    return len(args) == expected_length and all(arg.isdigit() or arg == '-' for arg in args[1:])

# Command: /set_max_health <base> <per_level> - Set max health
@dev_only
async def set_max_health(client: Client, message: Message):
    args = message.text.split()
    if not is_valid_numeric_input(args, 3):
        await message.reply_text("❌ Invalid Syntax: /set_max_health <base> <per_level>", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    try:
        base = int(args[1]) if args[1] != '-' else None
        per_level = int(args[2]) if args[2] != '-' else None
        
        config = load_json(CONFIG_FILE)
        if base is not None:
            config['max_health']['base'] = base
        if per_level is not None:
            config['max_health']['per_level'] = per_level

        save_json(CONFIG_FILE, config)
        await message.reply(f"<b>✅UPDATED</b>\n Max Health set: Base = {base if base else config['max_health']['base']} || Per Level = {per_level if per_level else config['max_health']['per_level']}.", parse_mode=ParseMode.HTML)
        logging.info(f"Max Health updated by {message.from_user.id} at {datetime.now()}.")
    except Exception as e:
        await message.reply_text("❌ An error occurred while setting max health.", parse_mode=ParseMode.HTML)
        logging.error(f"Error setting max health by {message.from_user.id} at {datetime.now()}: {e}")


# Command: /set_max_stamina <base> <per_level> - Set max stamina
@dev_only
async def set_max_stamina(client: Client, message: Message):
    args = message.text.split()
    if not is_valid_numeric_input(args, 3):
        await message.reply_text("❌ Invalid Syntax: /set_max_stamina <base> <per_level>", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    try:
        base = int(args[1]) if args[1] != '-' else None
        per_level = int(args[2]) if args[2] != '-' else None
        
        config = load_json(CONFIG_FILE)
        if base is not None:
            config['max_stamina']['base'] = base
        if per_level is not None:
            config['max_stamina']['per_level'] = per_level

        save_json(CONFIG_FILE, config)
        await message.reply(f"<b>✅UPDATED</b>\n Max Stamina set: Base = {base if base else config['max_stamina']['base']} || Per Level = {per_level if per_level else config['max_stamina']['per_level']}.", parse_mode=ParseMode.HTML)
        logging.info(f"Max Stamina updated by {message.from_user.id} at {datetime.now()}.")
    except Exception as e:
        await message.reply_text("❌ An error occurred while setting max stamina.", parse_mode=ParseMode.HTML)
        logging.error(f"Error setting max stamina by {message.from_user.id} at {datetime.now()}: {e}")


# Command: /set_stamina_usage <min> <max> - Set stamina usage
@dev_only
async def set_stamina_usage(client: Client, message: Message):
    args = message.text.split()
    if not is_valid_numeric_input(args, 3):
        await message.reply_text("❌ Invalid Syntax: /set_stamina_usage <min> <max>", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    try:
        min_usage = int(args[1]) if args[1] != '-' else None
        max_usage = int(args[2]) if args[2] != '-' else None
        
        config = load_json(CONFIG_FILE)
        if min_usage is not None:
            config['stamina_usage']['min'] = min_usage
        if max_usage is not None:
            config['stamina_usage']['max'] = max_usage

        save_json(CONFIG_FILE, config)
        await message.reply(f"<b>✅UPDATED</b>\n Stamina usage set: Min = {min_usage if min_usage else config['stamina_usage']['min']} || Max = {max_usage if max_usage else config['stamina_usage']['max']}.", parse_mode=ParseMode.HTML)
        logging.info(f"Stamina usage updated by {message.from_user.id} at {datetime.now()}.")
    except Exception as e:
        await message.reply_text("❌ An error occurred while setting stamina usage.", parse_mode=ParseMode.HTML)
        logging.error(f"Error setting stamina usage by {message.from_user.id} at {datetime.now()}: {e}")


# Command: /set_xp_gain <per_item> <per_encounter> <level_multiplier> - Set XP gain
@dev_only
async def set_xp_gain(client: Client, message: Message):
    args = message.text.split()
    if not is_valid_numeric_input(args, 4):
        await message.reply_text("❌ Invalid Syntax: /set_xp_gain <per_item> <per_encounter> <level_multiplier>", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    try:
        per_item = int(args[1]) if args[1] != '-' else None
        per_encounter = int(args[2]) if args[2] != '-' else None
        level_multiplier = int(args[3]) if args[3] != '-' else None
        
        config = load_json(CONFIG_FILE)
        if per_item is not None:
            config['xp_gain']['per_item'] = per_item
        if per_encounter is not None:
            config['xp_gain']['per_encounter'] = per_encounter
        if level_multiplier is not None:
            config['xp_gain']['level_multiplier'] = level_multiplier

        save_json(CONFIG_FILE, config)
        await message.reply(f"<b>✅UPDATED</b>\n XP Gain set: Per Item = {per_item if per_item else config['xp_gain']['per_item']}  Per Encounter = {per_encounter if per_encounter else config['xp_gain']['per_encounter']}, Level Multiplier = {level_multiplier if level_multiplier else config['xp_gain']['level_multiplier']}.", parse_mode=ParseMode.HTML)
        logging.info(f"XP Gain updated by {message.from_user.id} at {datetime.now()}.")
    except Exception as e:
        await message.reply_text("❌ An error occurred while setting XP gain.", parse_mode=ParseMode.HTML)
        logging.error(f"Error setting XP gain by {message.from_user.id} at {datetime.now()}: {e}")


# Command: /set_level_requirements <xp_per_level> <xp_increment_per_level> <level_cap> - Set level requirements
@dev_only
async def set_level_requirements(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2 or len(args) > 4 or not all(arg.isdigit() or arg == '-' for arg in args[1:]):
        await message.reply_text("❌ Invalid Syntax: /set_level_requirements <xp_per_level> <xp_increment_per_level> <level_cap>", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    try:
        xp_per_level = int(args[1]) if args[1] != '-' else None
        xp_increment_per_level = int(args[2]) if args[2] != '-' else None
        level_cap = int(args[3]) if args[3] != '-' else None
        
        config = load_json(CONFIG_FILE)
        if xp_per_level is not None:
            config['level_requirements']['xp_per_level'] = xp_per_level
        if xp_increment_per_level is not None:
            config['level_requirements']['xp_increment_per_level'] = xp_increment_per_level
        if level_cap is not None:
            config['level_requirements']['level_cap'] = level_cap

        save_json(CONFIG_FILE, config)
        await message.reply(f"<b>✅UPDATED</b>\n Level Requirements set: XP per Level = {xp_per_level if xp_per_level else config['level_requirements']['xp_per_level']}, XP Increment per Level = {xp_increment_per_level if xp_increment_per_level else config['level_requirements']['xp_increment_per_level']}, Level Cap = {level_cap if level_cap else config['level_requirements']['level_cap']}.", parse_mode=ParseMode.HTML)
        logging.info(f"Level Requirements updated by {message.from_user.id} at {datetime.now()}.")
    except Exception as e:
        await message.reply_text("❌ An error occurred while setting level requirements.", parse_mode=ParseMode.HTML)
        logging.error(f"Error setting level requirements by {message.from_user.id} at {datetime.now()}: {e}")


# Command: /set_space_per_item <common> <rare> <legendary> - Set space per item
@dev_only
async def set_space_per_item(client: Client, message: Message):
    args = message.text.split()
    if not is_valid_numeric_input(args, 4):
        await message.reply_text("❌ Invalid Syntax: /set_space_per_item <common> <rare> <legendary>", parse_mode=ParseMode.HTML)
        logging.error(f"Invalid command usage by {message.from_user.id} at {datetime.now()}: {message.text}")
        return

    try:
        common = int(args[1]) if args[1] != '-' else None
        rare = int(args[2]) if args[2] != '-' else None
        legendary = int(args[3]) if args[3] != '-' else None
        
        config = load_json(CONFIG_FILE)
        if common is not None:
            config['space_per_item']['common'] = common
        if rare is not None:
            config['space_per_item']['rare'] = rare
        if legendary is not None:
            config['space_per_item']['legendary'] = legendary

        save_json(CONFIG_FILE, config)
        await message.reply(f"<b>✅UPDATED</b>\n Space per Item set: Common = {common if common else config['space_per_item']['common']}, Rare = {rare if rare else config['space_per_item']['rare']}, Legendary = {legendary if legendary else config['space_per_item']['legendary']}.", parse_mode=ParseMode.HTML)
        logging.info(f"Space per Item updated by {message.from_user.id} at {datetime.now()}.")
    except Exception as e:
        await message.reply_text("❌ An error occurred while setting space per item.", parse_mode=ParseMode.HTML)
        logging.error(f"Error setting space per item by {message.from_user.id} at {datetime.now()}: {e}")

# Command: /sconfig - Show current configuration
@dev_only
async def show_config(client: Client, message: Message):
    """Send a preview of current configurations with buttons to navigate."""
    config = load_json(CONFIG_FILE)
    
    # Format config preview (you can format this better based on your needs)
    config_preview = json.dumps(config, indent=4)
    chunk_size = 3000  # Text size limit in Telegram
    config_chunks = [config_preview[i:i+chunk_size] for i in range(0, len(config_preview), chunk_size)]
    
    # Create inline buttons to navigate through config chunks
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Commands", callback_data="view_commands")]
    ])
    
    # Send the first part of the configuration preview
    await message.reply(
        f"Current configurations:\n<pre>{config_chunks[0]}</pre>",
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )

@dev_only
async def navigate_config(client: Client, callback_query: CallbackQuery):
    """Handle navigation through config chunks."""
    action = callback_query.data.split("_")
    if action[0] == "next" and action[1] == "config":
        chunk_number = int(action[2]) - 1
        config = load_json(CONFIG_FILE)
        config_preview = json.dumps(config, indent=4)
        chunk_size = 3000  # Text size limit in Telegram
        config_chunks = [config_preview[i:i+chunk_size] for i in range(0, len(config_preview), chunk_size)]
        
        await callback_query.message.edit_text(
            f"Current configurations:\n<pre>{config_chunks[chunk_number]}</pre>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Commands", callback_data="view_commands")]
            ])
        )

@dev_only
async def view_commands(client: Client, callback_query: CallbackQuery):
    """Handle the callback to show a list of commands and their syntax."""
    commands_message = (
        "Available Commands and their syntax:\n\n"
        "1. Max Health\n"
        "2. Max Stamina\n"
        "3. Stamina Usage\n"
        "4. XP Gain\n"
        "5. XP Value\n"
        "6. Level Requirements\n"
        "7. Space Per Item\n\n"
    )

    # Buttons for each command category
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Max Health", callback_data="command_1"),
         InlineKeyboardButton("Max Stamina", callback_data="command_2")],
        [InlineKeyboardButton("Stamina Usage", callback_data="command_3"),
         InlineKeyboardButton("XP Gain", callback_data="command_4")],
        [InlineKeyboardButton("XP Value", callback_data="command_5"),
         InlineKeyboardButton("Level Requirements", callback_data="command_6")],
        [InlineKeyboardButton("Space Per Item", callback_data="command_7"),
         InlineKeyboardButton("Show Config", callback_data="show_config")]
    ])
    # Send the message with buttons
    await callback_query.message.edit_text(
        commands_message,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )

# Command details with Next and Previous navigation
@dev_only
async def command_details(client: Client, callback_query: CallbackQuery):
    """Provide details for the clicked command."""
    command = callback_query.data.split("_")[1]  # Extract command index
    
    # Command descriptions
    command_descriptions = {
    "1": (
        "🔹 <b>Max Health</b>\n"
        "<b>What it does:</b> Sets the maximum health for the player.\n"
        "<b>Usage:</b> <code>/set_max_health &lt;base&gt; &lt;per_level&gt;</code>\n"
        "<b>Example:</b> <code>/set_max_health 50 2</code>\n\n"
        " This will set base health to 50, increasing by 2 each level.\n"
        "- <i>Tip:</i> Use this command to balance early game difficulty or make leveling smoother.\n\n"
    ),
    "2": (
        "🔹 <b>Max Stamina</b>\n\n"
        "<b>What it does:</b> Defines the player's stamina and how it increases per level.\n"
        "<b>Usage:</b> <code>/set_max_stamina &lt;base&gt; &lt;per_level&gt;</code>\n"
        "<b>Example:</b> <code>/set_max_stamina 50 2</code>\n"
        "- Sets the base stamina to 50, with an increase of 2 per level.\n"
        "- <i>Tip:</i> Adjust stamina for more challenging resource management or faster gameplay.\n\n"
    ),
    "3": (
        "🔹 <b>Stamina Usage</b>\n\n"
        "<b>What it does:</b> Adjusts the range for stamina consumption during actions.\n"
        "<b>Usage:</b> <code>/set_stamina_usage &lt;min&gt; &lt;max&gt;</code>\n"
        "<b>Example:</b> <code>/set_stamina_usage 1 5</code>\n"
        "- This sets the stamina usage between 1 and 5 for various actions.\n"
        "- <i>Tip:</i> Use this to create dynamic stamina consumption for different game mechanics (e.g., attacks, movement).\n\n"
    ),
    "4": (
        "🔹 <b>XP Gain</b>\n\n"
        "<b>What it does:</b> Adjusts the amount of XP gained from various in-game actions.\n"
        "<b>Usage:</b> <code>/set_xp_gain &lt;per_item&gt; &lt;per_encounter&gt; &lt;level_multiplier&gt;</code>\n"
        "<b>Example:</b> <code>/set_xp_gain 1 2 2</code>\n"
        "- Grants 1 XP per item, 2 XP per encounter, and doubles XP gained at each level.\n"
        "- <i>Tip:</i> Modify XP settings to slow down or accelerate progression based on game design.\n\n"
    ),
    "5": (
        "🔹 <b>XP Value</b>\n\n"
        "<b>What it does:</b> Defines the base XP value required for leveling up.\n"
        "<b>Usage:</b> <code>/set_xp_value &lt;value&gt;</code>\n"
        "<b>Example:</b> <code>/set_xp_value 0</code>\n"
        "- Sets the XP threshold to 0.\n"
        "- <i>Tip:</i> Adjust this value to control when players start gaining XP and to adjust level progression.\n\n"
    ),
    "6": (
        "🔹 <b>Level Requirements</b>\n\n"
        "<b>What it does:</b> Sets the XP required to level up and how it increases per level.\n"
        "<b>Usage:</b> <code>/set_level_requirements &lt;xp_per_level&gt; &lt;xp_increment_per_level&gt; &lt;level_cap&gt;</code>\n"
        "<b>Example:</b> <code>/set_level_requirements 100 10 50</code>\n"
        "- Requires 100 XP per level, increases by 10 XP per level, with a level cap of 50.\n"
        "- <i>Tip:</i> Adjust these values to create a progressive difficulty curve or adjust the pace of leveling.\n\n"
    ),
    "7": (
        "🔹 <b>Space Per Item</b>\n\n"
        "<b>What it does:</b> Adjusts the inventory space required for different item rarities.\n"
        "<b>Usage:</b> <code>/set_space_per_item &lt;common&gt; &lt;rare&gt; &lt;legendary&gt;</code>\n"
        "<b>Example:</b> <code>/set_space_per_item 1 2 3</code>\n"
        "- Sets 1 space for common items, 2 for rare items, and 3 for legendary items.\n"
        "- <i>Tip:</i> Modify these values to balance the weight of items and manage inventory size.\n\n"
    )
}

    
    # Show command details with a "Next" button to view the next command
    next_command = int(command) + 1 if int(command) < 7 else 1
    previous_command = int(command) - 1 if int(command) > 1 else 7
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Prev", callback_data=f"command_{previous_command}")],
        [InlineKeyboardButton("Next", callback_data=f"command_{next_command}")],
        [InlineKeyboardButton("Cmds", callback_data="view_commands")]
    ])
    
    # Send the details message with buttons
    await callback_query.message.edit_text(
        command_descriptions.get(command, "Invalid command selected."),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard
    )

# For testing purposes, let's add a logging function to print the callback data
@dev_only
async def log_callback_data(client: Client, callback_query: CallbackQuery):
    """Log callback query data to help debug the issue."""
    print(f"Callback query data: {callback_query.data}")
    await callback_query.answer()  # Respond to acknowledge the callback


# Register the handlers
def register(app: Client):
    app.add_handler(MessageHandler(dev, filters.command("dev")))
    app.add_handler(MessageHandler(delete_player_data, filters.command("delete_player")))
    app.add_handler(MessageHandler(set_max_health, filters.command("set_max_health")))
    app.add_handler(MessageHandler(set_max_stamina, filters.command("set_max_stamina")))
    app.add_handler(MessageHandler(set_stamina_usage, filters.command("set_stamina_usage")))
    app.add_handler(MessageHandler(set_xp_gain, filters.command("set_xp_gain")))
    app.add_handler(MessageHandler(set_level_requirements, filters.command("set_level_requirements")))
    app.add_handler(MessageHandler(set_space_per_item, filters.command("set_space_per_item")))
    app.add_handler(MessageHandler(show_config, filters.command("sconfig")))
    app.add_handler(CallbackQueryHandler(view_commands, filters.regex("view_commands")))  # Handle button click for commands
    app.add_handler(CallbackQueryHandler(command_details, filters.regex("command_")))  # Handle button click for command details

