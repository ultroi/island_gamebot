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

async def start(_, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Load player data or create a new player
    player = await load_player(user_id)
    if player:
        # Existing player: prompt to start a new arc and additional options for Settings and Support
        keyboard = [
            [InlineKeyboardButton("🆕 Start a New Adventure", callback_data='confirm_new_arc')],
            [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
            [InlineKeyboardButton("💬 Support", url='https://t.me/SurvivalSupportbot')]  # Link to support bot
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


async def button(client: Client, query: CallbackQuery):
    await query.answer()  # Acknowledge the callback query

    try:
        if query.data == 'start_adventure':
            await show_game_brief(query)

        elif query.data == 'confirm_new_arc':
            # Show options for selecting new arc (Survival or Narrative)
            arc_keyboard = [
                [InlineKeyboardButton("🏝️ Start Survival Arc", callback_data='start_survival_arc')],
                [InlineKeyboardButton("📖 Start Narrative Arc (Coming Soon)", callback_data='start_narrative_arc')]
            ]
            arc_markup = InlineKeyboardMarkup(arc_keyboard)
            await query.message.edit_text(
                "⚠️ Choose the arc to start. Starting a new arc will erase any current progress.",
                reply_markup=arc_markup, parse_mode=ParseMode.HTML
            )

        elif query.data == 'start_survival_arc':
            # Start the Survival Arc and reset any existing progress
            player = Player(user_id=query.from_user.id, name=query.from_user.first_name)
            await save_player(player)
            await query.message.edit_text("🆕 Starting a new Survival Arc! Let’s see how you fare this time.")
            await show_game_brief(query)  # Transition to game brief

        elif query.data == 'start_narrative_arc':
            # Placeholder for Narrative Arc (Coming Soon)
            await query.message.edit_text(
                "📖 <b>Narrative Arc Coming Soon!</b>\n\n"
                "Get ready for a unique, story-driven adventure where your choices shape the journey.",
                parse_mode=ParseMode.HTML
            )

        elif query.data == 'solo_arc':
            # Start Solo Arc
            player = Player(user_id=query.from_user.id, name=query.from_user.first_name, arc_type='solo', started_adventure=True)
            await save_player(player)
            await query.message.edit_text("🧭 Starting Solo Expedition! Let’s see how you fare on your own.")
            await explore(client, query.message)

        elif query.data == 'settings':
            # Handle settings (you can add functionality here)
            await query.message.edit_text(
                "⚙️ <b>Settings</b>\n\nHere you can configure your preferences or manage your account.",
                parse_mode=ParseMode.HTML
            )

    except Exception as e:
        await query.message.edit_text(f"⚠️ An error occurred: {str(e)}")  # Edit the message instead of sending a new one


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
        [InlineKeyboardButton("📜 Story Adventure", callback_data='narrative_arc')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=game_brief, reply_markup=reply_markup, parse_mode=ParseMode.HTML)


# Register function to attach the start and callback query handlers
def register(app: Client):
    app.on_message(filters.command("start"))(start)
    app.on_callback_query(filters.create(maintenance_mode_only) & filters.create(user_verification))(button)
