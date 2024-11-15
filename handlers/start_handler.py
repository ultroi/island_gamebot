from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.enums import ParseMode
from models.player import Player
from utils.db_utils import load_player, save_player, delete_player_progress
from handlers.adventure_handler import explore
from utils.decorators import user_verification, maintenance_mode_only

# Messages
START_MESSAGE = (
    "🏝️ <b>Welcome to Island Survival Bot!</b> 🏝️\n\n"
    "You're stranded on a mysterious island. Explore, gather resources, and survive!\n\n"
    "Are you ready to start your adventure? 🌊🐚🌴"
)

RESTART_MESSAGE = (
    "🔄 <b>Welcome back!</b>\n\n"
    "You can:\n\n"
    "🌟 <b>Continue your adventure</b>,\n"
    "🆕 <b>Start a new adventure</b>, or\n"
    "📖 <b>Switch to the Narrative Arc</b> (Coming Soon).\n\n"
    "Choose below!"
)

async def start(client: Client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Load player data or create a new player
    player = await load_player(user_id)
    if player:
        # Existing player: prompt to continue or start a new arc
        keyboard = [
            [InlineKeyboardButton("🔄 Continue Current Adventure", callback_data='continue_arc')],
            [InlineKeyboardButton("🆕 Start New Arc", callback_data='confirm_new_arc')],
            [InlineKeyboardButton("📖 Switch to Narrative Arc (Coming Soon)", callback_data='narrative_arc')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(RESTART_MESSAGE, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        # New player: prompt to start adventure
        player = Player(user_id=user_id, name=user_name)
        await save_player(player)
        keyboard = [
            [InlineKeyboardButton("🌊 Start Adventure", callback_data='start_adventure')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await message.reply_text(START_MESSAGE, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# Callback query handler
async def button(client: Client, query: CallbackQuery):
    await query.answer()  # Acknowledge the callback query

    try:
        if query.data == 'start_adventure':
            await show_game_brief(query)

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
                "⚠️ Are you sure you want to start a new arc? This will erase your current progress.",
                reply_markup=confirm_markup, parse_mode=ParseMode.HTML
            )

        elif query.data == 'choose_arc_restart':
            arc_keyboard = [
                [InlineKeyboardButton("🏝️ Restart Survival Arc", callback_data='restart_survival_arc')],
                [InlineKeyboardButton("📖 Restart Narrative Arc (Coming Soon)", callback_data='restart_narrative_arc')]
            ]
            arc_markup = InlineKeyboardMarkup(arc_keyboard)
            await query.message.reply_text(
                "Select the arc you wish to restart. This will erase your progress in the specific arc.",
                reply_markup=arc_markup, parse_mode=ParseMode.HTML
            )

        elif query.data == 'restart_survival_arc':
            await delete_player_progress(query.from_user.id, arc_type='survival')
            player = Player(user_id=query.from_user.id, name=query.from_user.first_name)  # Reinitialize player for new survival arc
            await save_player(player)
            await query.message.reply_text("🆕 Starting a new Survival Arc! Let’s see how you fare this time.")
            await show_game_brief(query)

        elif query.data == 'narrative_arc' or query.data == 'restart_narrative_arc':
            await query.message.reply_text(
                "📖 <b>Narrative Arc Coming Soon!</b>\n\n"
                "Get ready for a unique, story-driven adventure where your choices shape the journey.",
                parse_mode=ParseMode.HTML
            )

        elif query.data == 'solo_arc':
            await explore(client, query.message)

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

async def show_game_brief(query: CallbackQuery):
    # Show a brief introduction to the game when starting a new arc or adventure
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
    await query.edit_message_text(text=game_brief, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# Register function to attach the start and callback query handlers
def register(app: Client):
    app.on_message(filters.command("start"))(start)
    app.on_callback_query(filters.create(maintenance_mode_only) & filters.create(user_verification))(button)
