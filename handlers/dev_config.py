import logging
import json
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from pyrogram.enums import ParseMode
from utils.db_utils import get_all_players, delete_player  # Ensure these are correctly implemented
from utils.shared_utils import get_level_xp  # Ensure this is correctly implemented

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# List of developer user IDs (for authorization)
DEV_USER_IDS = [5956598856]  # Replace with actual developer IDs

# Paths to JSON files
CONFIG_FILE = "/workspaces/island_gamebot/data/config.json"
ITEM_FILE = "/workspaces/island_gamebot/data/items.json"
EXPLORATION_FILE = "exploration.json"

# Temporary configurations per developer
TEMP_CONFIGS = {}  # Key: user_id, Value: temp config dict
ORIGINAL_CONFIGS = {}  # Key: user_id, Value: original config dict

# Initialize the Pyrogram Client
app = Client("my_bot")

# Developer authorization decorator
def dev_only(func):
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        if message.from_user.id not in DEV_USER_IDS:
            await message.reply_text("🚫 **You are not authorized to use this command.**", parse_mode=ParseMode.MARKDOWN)
            logging.warning(f"Unauthorized access attempt by user {message.from_user.id}.")
            return
        return await func(client, message, *args, **kwargs)
    return wrapper

# Utility functions to read and write JSON files
def load_json(file_path: str) -> dict:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"{file_path} not found. Creating a new one.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Failed to parse {file_path}.")
        return {}

def save_json(file_path: str, data: dict):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    logging.info(f"Configuration saved to {file_path}.")

def validate_json_input(response: Message) -> dict:
    """Validates if the input is a valid JSON format."""
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        return None

async def broadcast_message(client: Client, message: str):
    """Broadcast a message to all users."""
    players = await get_all_players()
    if not players:
        logging.warning("No players to broadcast to.")
        return
    for player in players:
        try:
            await client.send_message(chat_id=player.user_id, text=message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logging.error(f"Failed to send message to {player.user_id}: {e}")
    logging.info("Broadcast message sent to all users.")

# Command: /dev - Display player information
@dev_only
async def dev(client: Client, message: Message):
    """Display information about all players."""
    players = await get_all_players()
    if not players:
        await message.reply_text("📭 **No players found.**", parse_mode=ParseMode.MARKDOWN)
        return

    player_info = "\n".join(
        [f"• **Name**: {player.name}, **ID**: `{player.user_id}`" for player in players]
    )
    await message.reply_text(f"📊 **Number of players:** {len(players)}\n\n{player_info}", parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Developer {message.from_user.id} accessed player information.")

# Command: /delete_player <user_id> - Delete a specific player's data
@dev_only
async def delete_player_data(client: Client, message: Message):
    """Delete a specific player's data by user ID."""
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply_text("❌ **Usage:** `/delete_player <user_id>`\n*(numeric)*", parse_mode=ParseMode.MARKDOWN)
        logging.error("Invalid /delete_player command usage.")
        return

    user_id = int(args[1])
    success = await delete_player(user_id)
    if success:
        await message.reply_text(f"✅ **Player data for user_id `{user_id}` has been deleted.**", parse_mode=ParseMode.MARKDOWN)
        logging.info(f"Developer {message.from_user.id} deleted player data for user_id {user_id}.")
    else:
        await message.reply_text(f"⚠️ **No player found with user_id `{user_id}`.**", parse_mode=ParseMode.MARKDOWN)
        logging.warning(f"Attempted to delete non-existent player with user_id {user_id}.")

# Command: /set_max_health <level> <value>
@dev_only
async def set_max_health(client: Client, message: Message):
    """Set the maximum health for players."""
    args = message.text.split()
    if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
        await message.reply_text("❌ **Usage:** `/set_max_health <level> <value>`\n*(numeric)*", parse_mode=ParseMode.MARKDOWN)
        logging.error("Invalid /set_max_health command usage.")
        return

    level, new_max_health = int(args[1]), int(args[2])
    config = load_json(CONFIG_FILE)

    if "max_health" not in config:
        config["max_health"] = {}

    config["max_health"][str(level)] = new_max_health
    save_json(CONFIG_FILE, config)

    await message.reply_text(f"✅ **Maximum health for level `{level}` set to `{new_max_health}`.**", parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Developer {message.from_user.id} set maximum health for level {level} to {new_max_health}.")

# Command: /set_stamina_usage <value>

@dev_only
async def set_stamina_usage(client: Client, message: Message):
    """Set the stamina usage for actions."""
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply_text("❌ **Usage:** `/set_stamina_usage <value>`\n*(numeric)*", parse_mode=ParseMode.MARKDOWN)
        logging.error("Invalid /set_stamina_usage command usage.")
        return

    stamina_usage = int(args[1])
    if stamina_usage < 0:
        await message.reply_text("❌ **Invalid value. Stamina usage must be a non-negative number.**", parse_mode=ParseMode.MARKDOWN)
        return

    config = load_json(CONFIG_FILE)
    config["stamina_usage"] = stamina_usage
    save_json(CONFIG_FILE, config)

    await message.reply_text(f"✅ **Stamina usage set to `{stamina_usage}`.**", parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Developer {message.from_user.id} set stamina usage to {stamina_usage}.")

# Command: /set_xp_gain <value>
@app.on_message(filters.command("set_xp_gain") & filters.private)
@dev_only
async def set_xp_gain(client: Client, message: Message):
    """Set the XP gain for actions."""
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply_text("❌ **Usage:** `/set_xp_gain <value>`\n*(numeric)*", parse_mode=ParseMode.MARKDOWN)
        logging.error("Invalid /set_xp_gain command usage.")
        return

    xp_gain = int(args[1])
    if xp_gain < 0:
        await message.reply_text("❌ **Invalid value. XP gain must be a non-negative number.**", parse_mode=ParseMode.MARKDOWN)
        return

    config = load_json(CONFIG_FILE)
    config["xp_gain"] = xp_gain
    save_json(CONFIG_FILE, config)

    await message.reply_text(f"✅ **XP gain set to `{xp_gain}`.**", parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Developer {message.from_user.id} set XP gain to {xp_gain}.")

# Command: /level_up_xp <current_level> - Calculate XP required to level up
@dev_only
async def set_get_level_xp(client: Client, message: Message):
    """Calculate the XP required to level up for a given current level."""
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply_text("❌ **Usage:** `/level_up_xp <current_level>`\n*(numeric)*", parse_mode=ParseMode.MARKDOWN)
        logging.error("Invalid /level_up_xp command usage.")
        return

    current_level = int(args[1])
    xp_required = get_level_xp(current_level)

    await message.reply_text(
        f"🎯 **XP required to level up from level `{current_level}` to level `{current_level + 1}`:** `{xp_required}` XP.",
        parse_mode=ParseMode.MARKDOWN
    )
    logging.info(f"Developer {message.from_user.id} requested XP calculation for level-up from level {current_level}.")

# Command: /item_config - Configure item settings

@dev_only
async def item_config(client: Client, message: Message):
    """Configure item settings."""
    await message.reply_text(
        "🛠️ **Item Configuration:**\n\n"
        "Enter the new item configuration in JSON format with the following structure:\n\n"
        "```json\n"
        "{\n"
        '    "items": [\n'
        '        {\n'
        '            "name": "Apple",\n'
        '            "category": "food",\n'
        '            "type": "common",\n'
        '            "space_per_item": 1,\n'
        '            "area": "inventory"\n'
        '        },\n'
        '        ...\n'
        '    ]\n'
        "}\n"
        "```",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_item_config_response(response: Message):
    if response.from_user.id != response.from_user.id:
        return

    item_config = validate_json_input(response)
    if item_config is None:
        await response.reply_text("❌ **Invalid JSON format. Please enter a valid JSON configuration.**", parse_mode=ParseMode.MARKDOWN)
        logging.error(f"Invalid JSON format for item configuration by user {response.from_user.id}.")
        return

    # Validate structure of the JSON
    if not isinstance(item_config, dict) or "items" not in item_config:
        await response.reply_text("❌ **Invalid configuration structure. Ensure the JSON contains an 'items' array.**", parse_mode=ParseMode.MARKDOWN)
        logging.error(f"Invalid configuration structure for item configuration by user {response.from_user.id}.")
        return

    # Validate each item
    for item in item_config["items"]:
        required_keys = ["name", "category", "type", "space_per_item", "area"]
        if not all(key in item for key in required_keys):
            await response.reply_text(
                "❌ **Each item must include 'name', 'category', 'type', 'space_per_item', and 'area'.**",
                parse_mode=ParseMode.MARKDOWN
            )
            logging.error(f"Missing required fields in item configuration: {item}")
            return

    # Validate category
        if item["category"] not in ["food", "non-food"]:
            await response.reply_text(
                f"❌ **Invalid category '{item['category']}' for item '{item['name']}'. It must be 'food' or 'non-food'.**",
                parse_mode=ParseMode.MARKDOWN
            )
        logging.error(f"Invalid category for item {item['name']}.")
        return

    # Validate type
        if item["type"] not in ["rare", "common"]:
            await response.reply_text(
            f"❌ **Invalid type '{item['type']}' for item '{item['name']}'. It must be 'rare' or 'common'.**",
            parse_mode=ParseMode.MARKDOWN
            )
            logging.error(f"Invalid type for item {item['name']}.")
            return

    # Validate space per item
        if not isinstance(item["space_per_item"], int) or item["space_per_item"] <= 0:
            await response.reply_text(
                f"❌ **Invalid 'space_per_item' value for item '{item['name']}'. It must be a positive integer.**",
                parse_mode=ParseMode.MARKDOWN
                )
            logging.error(f"Invalid space per item for item {item['name']}.")
            return

    # Save the new item configuration to the file
    save_json(ITEM_FILE, item_config)

    # Confirm the update
    await response.reply_text("✅ **Item configuration has been successfully updated.**", parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Developer {response.from_user.id} updated item configuration.")

     

# Command: /exploration_config - Configure exploration settings

@dev_only
async def exploration_config(client: Client, message: Message):
    """Configure exploration settings."""
    await message.reply_text(
        "🛠️ **Exploration Configuration:**\n\n"
        "Enter the new exploration configuration in JSON format with the desired structure.\n\n"
        "Example:\n\n"
        "```json\n"
        "{\n"
        '    "exploration_rates": {\n'
        '        "forest": 1.5,\n'
        '        "desert": 1.2\n'
        "    }\n"
        "}\n"
        "```",
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_exploration_config_response(client: Client, response: Message):
    if response.from_user.id != response.from_user.id:
        return

    exploration_config = validate_json_input(response)
    if exploration_config is None:
        await response.reply_text("❌ **Invalid JSON format. Please enter a valid JSON configuration.**", parse_mode=ParseMode.MARKDOWN)
        logging.error(f"Invalid JSON format for exploration configuration by user {response.from_user.id}.")
        return

        # Additional validation can be added here as needed

        # Save the new exploration configuration
    save_json(EXPLORATION_FILE, exploration_config)

        # Confirm the update
    await response.reply_text("✅ **Exploration configuration has been successfully updated.**", parse_mode=ParseMode.MARKDOWN)
    logging.info(f"Developer {response.from_user.id} updated exploration configuration.")


def register(app: Client):
    # Message Handlers
    app.on_message(filters.command("dev") & filters.private)(dev)
    app.on_message(filters.command("delete_player") & filters.private)(delete_player_data)
    app.on_message(filters.command("set_max_health") & filters.private)(set_max_health)
    app.on_message(filters.command("set_stamina_usage") & filters.private)(set_stamina_usage)
    app.on_message(filters.command("set_xp_gain") & filters.private)(set_xp_gain)
    app.on_message(filters.command("item_config") & filters.private)(item_config)
    app.on_message(filters.command("exploration_config") & filters.private)(exploration_config)