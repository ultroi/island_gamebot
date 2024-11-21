import logging
import json
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from handlers.dev_config import dev_only, broadcast_message
from pyrogram.enums import ParseMode
from main import app
 
DEV_USER_IDS = [5956598856]  # Replace with actual developer IDs

# Paths to JSON files
CONFIG_FILE = "/workspaces/island_gamebot/data/config.json"
ITEM_FILE = "/workspaces/island_gamebot/data/items.json"
EXPLORATION_FILE = "exploration.json"

# Temporary configurations per developer
TEMP_CONFIGS = {}  # Key: user_id, Value: temp config dict
ORIGINAL_CONFIGS = {}  # Key: user_id, Value: original config dict

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

# Command: /modify_config - Modify configurations via buttons
@app.on_message(filters.command("modify_config") & filters.private)
@dev_only
async def modify_config(client: Client, message: Message):
    """Enter the modify configuration mode."""
    user_id = message.from_user.id
    if user_id in TEMP_CONFIGS:
        await message.reply_text("⚠️ **You are already in configuration mode. Please apply or discard your current changes before starting a new session.**", parse_mode=ParseMode.MARKDOWN)
        return

    # Load current configuration
    current_config = load_json(CONFIG_FILE)
    TEMP_CONFIGS[user_id] = current_config.copy()
    ORIGINAL_CONFIGS[user_id] = current_config.copy()

    # Prepare display text
    config_text = "<b>📄 Current Configuration:</b>\n"
    for key, value in current_config.items():
        config_text += f"• <b>{key}</b>: `{value}`\n"

    # Inline keyboard with modification options
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔧 Set Max Health", callback_data="set_max_health"),
            InlineKeyboardButton("🔧 Set Stamina Usage", callback_data="set_stamina_usage"),
        ],
        [
            InlineKeyboardButton("🔧 Set XP Gain", callback_data="set_xp_gain"),
            InlineKeyboardButton("🔧 Set Level-Up XP", callback_data="set_level_up_xp"),
        ],
        [
            InlineKeyboardButton("✅ Apply Changes", callback_data="apply_changes"),
            InlineKeyboardButton("❌ Discard Changes", callback_data="discard_changes"),
        ],
    ])

    await message.reply_text(
        f"{config_text}\n\n<b>🔄 Select an option below to modify the configuration:</b>",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
    logging.info(f"Developer {user_id} entered configuration mode.")

 
@dev_only
async def handle_callback_query(client: Client, callback_query: CallbackQuery):
    """Handle button callbacks for modifying configurations."""
    user_id = callback_query.from_user.id
    data = callback_query.data

    if user_id not in TEMP_CONFIGS:
        await callback_query.answer("⚠️ **You are not in configuration mode. Use /modify_config to start.**", show_alert=True)
        return

    # Handle applying changes
    if data == "apply_changes":
        # Save the temp config to the main config file
        save_json(CONFIG_FILE, TEMP_CONFIGS[user_id])
        await callback_query.message.edit_text(
            "<b>✅ Changes have been applied successfully!</b>\n\nBroadcasting updates to all users...",
            parse_mode=ParseMode.HTML,
            reply_markup=None,
        )
        logging.info(f"Developer {user_id} applied configuration changes.")

        # Broadcast the update to all users
        await broadcast_message(client, "⚙️ **Configurations have been modified to maintain game balance.**")

        # Clear temporary configs
        del TEMP_CONFIGS[user_id]
        del ORIGINAL_CONFIGS[user_id]
        return

    # Handle discarding changes
    if data == "discard_changes":
        # Discard temporary changes
        del TEMP_CONFIGS[user_id]
        del ORIGINAL_CONFIGS[user_id]
        await callback_query.message.edit_text(
            "<b>❌ Changes have been discarded. Exiting configuration mode.</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=None,
        )
        logging.info(f"Developer {user_id} discarded configuration changes.")
        return

    # Handle specific configuration modifications
    instruction_map = {
        "set_max_health": (
            "<b>🔧 Modify Maximum Health:</b>\n\n"
            "Use the following command to set the maximum health for a specific level:\n\n"
            "• **Command:** `/set_max_health <level> <value>`\n"
            "• **Example:** `/set_max_health 10 500`\n\n"
            "This command sets the maximum health for level 10 to 500."
        ),
        "set_stamina_usage": (
            "<b>🔧 Modify Stamina Usage:</b>\n\n"
            "Use the following command to set the stamina usage for actions:\n\n"
            "• **Command:** `/set_stamina_usage <value>`\n"
            "• **Example:** `/set_stamina_usage 20`\n\n"
            "This command sets the stamina usage to 20."
        ),
        "set_xp_gain": (
            "<b>🔧 Modify XP Gain:</b>\n\n"
            "Use the following command to set the XP gain for actions:\n\n"
            "• **Command:** `/set_xp_gain <value>`\n"
            "• **Example:** `/set_xp_gain 100`\n\n"
            "This command sets the XP gain to 100."
        ),
        "set_level_up_xp": (
            "<b>🔧 Modify Level-Up XP:</b>\n\n"
            "Use the following command to set the XP required to level up from a specific level:\n\n"
            "• **Command:** `/level_up_xp <current_level> <required_xp>`\n"
            "• **Example:** `/level_up_xp 10 200`\n\n"
            "This command sets the XP required to level up from level 10 to 200."
        ),
    }

    # Show instructions for specific setting modifications
    if data in instruction_map:
        instruction = instruction_map[data]

        # Inline keyboard with Save and Back buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💾 Save Change", callback_data=f"save_{data}"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_menu"),
            ]
        ])

        await callback_query.message.edit_text(
            instruction,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
        logging.info(f"Developer {user_id} requested instructions for {data}.")
        return

    # Handle Save button for specific settings
    if data.startswith("save_"):
        setting = data.split("_")[1]
        # Since actual saving is done via commands, here we just acknowledge
        await callback_query.answer(f"🔄 **Please use the corresponding command to save this setting.**", show_alert=True)
        logging.info(f"Developer {user_id} attempted to save {setting} via button (not allowed).")
        return

    # Handle Back to main menu
    if data == "back_to_menu":
        config = TEMP_CONFIGS[user_id]
        config_text = "<b>📄 Current Configuration:</b>\n"
        for key, value in config.items():
            config_text += f"• <b>{key}</b>: `{value}`\n"

        # Inline keyboard with modification options
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 Set Max Health", callback_data="set_max_health"),
                InlineKeyboardButton("🔧 Set Stamina Usage", callback_data="set_stamina_usage"),
            ],
            [
                InlineKeyboardButton("🔧 Set XP Gain", callback_data="set_xp_gain"),
                InlineKeyboardButton("🔧 Set Level-Up XP", callback_data="set_level_up_xp"),
            ],
            [
                InlineKeyboardButton("✅ Apply Changes", callback_data="apply_changes"),
                InlineKeyboardButton("❌ Discard Changes", callback_data="discard_changes"),
            ],
        ])

        await callback_query.message.edit_text(
            f"{config_text}\n\n<b>🔄 Select an option below to modify the configuration:</b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
        logging.info(f"Developer {user_id} returned to configuration menu.")

        

# Register function to add handlers in main.py
def register(app: Client):
    app.on_message(filters.command("modify_config") & filters.private)(modify_config)
    app.on_callback_query(
        filters.regex("set_max_health|set_stamina_usage|set_xp_gain|set_level_up_xp|confirm_changes|cancel_changes")
    )(handle_callback_query)
    
 