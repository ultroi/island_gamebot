from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.enums import ParseMode
from models.player import Player
from handlers.error_handler import error_handler_decorator
from utils.db_utils import load_player, save_player, delete_player_progress
from handlers.adventure_handler import explore
from utils.decorators import maintenance_mode_only
import logging

# Constants for messages
START_MESSAGE = (
    "🌴🏝️ <b>Welcome to Island Survival Bot!</b> 🏝️🌴\n\n"
    "You're marooned on a mysterious, untamed island where adventure awaits at every turn! 🌊🐚\n\n"
    "💡 <b>Your Goal:</b> Survive, thrive, and uncover the island's secrets. 🌟\n\n"
    "🌟 Will you explore the dense jungles, brave the wild animals, or uncover hidden treasures?\n\n"
    "🧭 <b>Your journey begins now.</b> Are you ready to face the unknown? Let's get started!"
)

RESTART_MESSAGE = (
    "🌟🔄 <b>Welcome back to Island Survival!</b> 🔄🌟\n\n"
    "Your adventure continues...\n\n"
    "🏝️ <b>Keep exploring</b>, gathering resources, and outsmarting the dangers of the island.\n\n"
    "🆕 <b>Want a fresh start?</b> Begin a new journey and rewrite your survival story!\n\n"
    "⚡ What will you do next? Your fate is in your hands. Choose an option below to decide your path:"
)


SETTINGS_MESSAGE = (
    "⚙️ <b>Settings</b>\n\n"
    "Here you can configure your preferences:\n\n"
    "🔔 Enable/Disable Notifications\n"
    "🌐 Change Language\n"
    "🔄 Reset Progress\n\n"
    "Select an option below to manage your account."
)

@error_handler_decorator
async def start(_, message: Message):
    """Handles the /start command."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    logging.info(f"User {user_name} ({user_id}) issued /start command.")

    # Load player data or create a new player
    player = await load_player(user_id)
    if player:
        # Existing player: prompt to continue or start a new adventure
        keyboard = [
            [InlineKeyboardButton("🆕 Start New Adventure", callback_data='confirm_new_arc'),
             InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
            [InlineKeyboardButton("💬 Support", url='https://t.me/SurvivalSupportbot')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(RESTART_MESSAGE, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        # New player: create and prompt to start adventure
        player = Player(user_id=user_id, name=user_name)
        await save_player(player.user_id, player)
        keyboard = [
            [InlineKeyboardButton("🌊 Start Adventure", callback_data='start_adventure')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(START_MESSAGE, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@error_handler_decorator
async def show_game_brief(query: CallbackQuery):
    """Displays the game introduction and adventure options."""
    game_brief = (
        "🏝️ <b>Island Survival Adventure</b> 🏝️\n\n"
        "As a <b>castaway</b>, you must explore the island to find <b>essential items, food,</b> and <b>shelter</b> to survive.\n\n"
        "🌍 Explore diverse locations like the Beach, Forest, and Mountains.\n"
        "🔍 Gather resources and manage your health.\n"
        "⚔️ Beware of dangerous encounters.\n\n"
        "Choose your adventure below!"
    )
    keyboard = [
        [InlineKeyboardButton("🧭 Solo Expedition", callback_data='solo_arc')],
        [InlineKeyboardButton("📜 Story Adventure", callback_data='start_narrative_arc')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=game_brief, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@error_handler_decorator
async def confirm_new_arc(query: CallbackQuery):
    """Prompts user to confirm starting a new arc."""
    keyboard = [
        [InlineKeyboardButton("🏝️ Start Survival Arc", callback_data='start_survival_arc')],
        [InlineKeyboardButton("📖 Start Narrative Arc (Coming Soon)", callback_data='start_narrative_arc')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(
        "⚠️ Starting a new arc will erase any current progress.\n\n"
        "Select an arc to proceed.",
        reply_markup=reply_markup, parse_mode=ParseMode.HTML
    )

@error_handler_decorator
async def start_survival_arc(query: CallbackQuery):
    """Starts a new Survival Arc."""
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    player = Player(user_id=user_id, name=user_name)
    await save_player(player)

    await query.message.edit_text(
        "🆕 Starting a new Survival Arc! Let’s see how you fare this time.",
        parse_mode=ParseMode.HTML
    )
    await show_game_brief(query)

@error_handler_decorator
async def show_narrative_placeholder(query: CallbackQuery):
    """Shows a placeholder for the narrative arc."""
    await query.message.edit_text(
        "📖 <b>Narrative Arc Coming Soon!</b>\n\n"
        "Get ready for a unique, story-driven adventure where your choices shape the journey.",
        parse_mode=ParseMode.HTML
    )

@error_handler_decorator
async def start_solo_arc(client: Client, query: CallbackQuery):
    """Starts a Solo Expedition."""
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    player = Player(user_id=user_id, name=user_name, arc_type='solo', started_adventure=True)
    await save_player(player)

    await query.message.edit_text("🧭 Starting Solo Expedition! Let’s see how you fare on your own.")
    await explore(client, query.message)

@error_handler_decorator
async def show_settings(query: CallbackQuery):
    """Displays settings options."""
    keyboard = [
        [InlineKeyboardButton("🔔 Toggle Notifications", callback_data='settings_toggle_notifications')],
        [InlineKeyboardButton("🌐 Change Language", callback_data='settings_change_language')],
        [InlineKeyboardButton("🔄 Reset Progress", callback_data='settings_reset_progress')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(SETTINGS_MESSAGE, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
