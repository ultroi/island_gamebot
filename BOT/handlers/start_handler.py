# handlers/start_handler.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from models.player import Player
from BOT import app
from utils.db_utils import load_player, save_player, delete_player_progress
from handlers.adventure_handler import explore
from utils.decorators import user_verification, maintenance_mode_only

START_MESSAGE = (
    "🏝️ <b>Welcome to Island Survival Bot!</b> 🏝️\n\n"
    "You've found yourself <b>stranded on a mysterious island</b> with only limited supplies. "
    "Survival depends on your ability to <b>explore</b>, <b>gather resources</b>, and overcome the challenges "
    "hidden in every corner of the island. 🌊🐚🌴\n\n"
    "Are you ready to begin your adventure? 🧭"
)

RESTART_MESSAGE = (
    "🔄 <b>Welcome back to the Island Survival Adventure!</b>\n\n"
    "It seems you've already started your survival journey! Would you like to:\n\n"
    "🌟 <b>Continue your current adventure</b> to pick up where you left off,\n"
    "🆕 <b>Start a new arc</b> to reset and face new challenges, or\n"
    "📖 <b>Switch to the Narrative Arc</b> for a story-based adventure.\n\n"
    "Choose one of the options below to continue!"
)

@maintenance_mode_only
@user_verification
@app.on_message(filters.command("start"))
async def start(client, message):
    print("Start command received!")
    """
    Handle the /start command. Greets the user and presents options based on their player status.

    Args:
        client (Client): The pyrogram client.
        message (Message): Incoming message from Telegram.
    """
    user_id = message.from_user.id
    user_name = message.from_user.first_name  # Get the user's Telegram first name

    player = load_player(user_id)
    if player:
        # Player already exists, present options for continuing, restarting, or switching to narrative
        keyboard = [
            [InlineKeyboardButton("🔄 Continue Current Adventure", callback_data='continue_arc')],
            [InlineKeyboardButton("🆕 Start New Arc", callback_data='confirm_new_arc')],
            [InlineKeyboardButton("📖 Switch to Narrative Arc (Coming Soon)", callback_data='narrative_arc')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(RESTART_MESSAGE, reply_markup=reply_markup, parse_mode='html')
    else:
        # New player, show the start message and Start Adventure button
        player = Player(user_id, name=user_name)
        await save_player(player)

        keyboard = [
            [InlineKeyboardButton("🌊 Start Adventure", callback_data='start_adventure')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(START_MESSAGE, reply_markup=reply_markup, parse_mode='html')


@app.on_callback_query(filters.create(maintenance_mode_only) & filters.create(user_verification))
async def button(client, query: CallbackQuery):
    await query.answer()

    try:
        if query.data == 'start_adventure':
            game_brief = (
                "🏝️ <b>Island Survival Adventure</b> 🏝️\n\n"
                "As a <b>castaway</b>, you must explore the island to find <b>essential items, food,</b> and <b>shelter</b> to survive.\n\n"
                "<b>Your Adventure Includes:</b>\n"
                "🧭 <b>Exploration</b>: Traverse diverse locations like the <b>Beach</b>, <b>Forest</b>, <b>Mountains</b>, and an <b>Ancient Temple</b>.\n\n"
                "🔍 <b>Resource Gathering</b>: Collect unique items at each location.\n\n"
                "⚔️ <b>Encounters</b>: Beware! You may face wild animals or mysterious events.\n\n"
                "🎒 <b>Inventory & Health</b>: Carefully manage your health and inventory.\n\n"
                "<b>Will you thrive, or will the island’s mysteries be your end? Let’s start your survival journey!</b>"
            )
            keyboard = [
                [InlineKeyboardButton("🧭 Solo Expedition", callback_data='solo_arc')],
                [InlineKeyboardButton("📜 Story Adventure (Coming Soon)", callback_data='narrative_arc')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=game_brief, reply_markup=reply_markup, parse_mode='html')

        elif query.data == 'continue_arc':
            await query.message.edit_text("🔄 Resuming your current adventure! Let’s pick up where we left off.")
            await explore(client, query.message)

        elif query.data == 'confirm_new_arc':
            confirm_keyboard = [
                [InlineKeyboardButton("🆕 Confirm Restart", callback_data='choose_arc_restart')],
                [InlineKeyboardButton("❌ Cancel", callback_data='cancel_restart')]
            ]
            confirm_markup = InlineKeyboardMarkup(confirm_keyboard)
            await query.message.reply_text(
                "⚠️ Are you sure you want to start a new arc? This will erase your current progress in the selected arc.",
                reply_markup=confirm_markup, parse_mode='html'
            )

        elif query.data == 'choose_arc_restart':
            arc_keyboard = [
                [InlineKeyboardButton("🏝️ Restart Survival Arc", callback_data='restart_survival_arc')],
                [InlineKeyboardButton("📖 Restart Narrative Arc (Coming Soon)", callback_data='restart_narrative_arc')]
            ]
            arc_markup = InlineKeyboardMarkup(arc_keyboard)
            await query.message.reply_text(
                "Select the arc you wish to restart. This will erase your progress in the specific arc.",
                reply_markup=arc_markup, parse_mode='html'
            )

        elif query.data == 'restart_survival_arc':
            await delete_player_progress(query.from_user.id, arc_type='survival', context=client)
            player = Player(query.from_user.id)  # Reinitialize player for new survival arc
            await save_player(player)
            await query.message.reply_text("🆕 Starting a new Survival Arc! Let’s see how you fare this time.")
            game_brief = (
                "🏝️ <b>Island Survival Adventure</b> 🏝️\n\n"
                "As a <b>castaway</b>, you must explore the island to find <b>essential items, food,</b> and <b>shelter</b> to survive.\n\n"
                "<b>Your Adventure Includes:</b>\n"
                "🧭 <b>Exploration</b>: Traverse diverse locations like the <b>Beach</b>, <b>Forest</b>, <b>Mountains</b>, and an <b>Ancient Temple</b>.\n\n"
                "🔍 <b>Resource Gathering</b>: Collect unique items at each location.\n\n"
                "⚔️ <b>Encounters</b>: Beware! You may face wild animals or mysterious events.\n\n"
                "🎒 <b>Inventory & Health</b>: Carefully manage your health and inventory.\n\n"
                "<b>Will you thrive, or will the island’s mysteries be your end? Let’s start your survival journey!</b>"
            )
            keyboard = [
                [InlineKeyboardButton("🧭 Solo Expedition", callback_data='solo_arc')],
                [InlineKeyboardButton("📜 Story Adventure (Coming Soon)", callback_data='narrative_arc')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=game_brief, reply_markup=reply_markup, parse_mode='html')

        elif query.data == 'restart_narrative_arc' or query.data == 'narrative_arc':
            await query.message.reply_text(
                "📖 <b>Narrative Arc Coming Soon!</b>\n\n"
                "Get ready for a unique, story-driven adventure where your choices shape the journey.",
                parse_mode='html'
            )

        elif query.data == 'solo_arc':
            await explore(client, query.message)  # Start exploration for Solo Arc

        elif query.data == 'explore_again':
            await explore(client, query.message)  # Explore again for Solo Arc

        elif query.data == 'cancel_restart':
            initial_keyboard = [
                [InlineKeyboardButton("▶️ Continue", callback_data='continue_arc')],
                [InlineKeyboardButton("🔄 New Arc", callback_data='confirm_new_arc')],
                [InlineKeyboardButton("🔀 Switch Arc", callback_data='narrative_arc')]
            ]
            initial_markup = InlineKeyboardMarkup(initial_keyboard)
            await query.message.reply_text(
                "Action canceled. You’re still in your current adventure.",
                reply_markup=initial_markup
            )

    except Exception as e:
        await query.message.reply_text(f"⚠️ An error occurred: {str(e)}")
