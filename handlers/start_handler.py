import asyncio
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.enums import ParseMode
from models.player import Player
from handlers.error_handler import error_handler_decorator
from utils.db_utils import load_player, save_player
from handlers.adventure_handler import explore  # Import the explore command

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

SETTINGS_MESSAGE = "⚙️ <b>Settings</b>\n\nThis section is under development. Stay tuned!"

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

        # Send image first, without the caption
        sent_message = await message.reply_photo(
            photo='https://files.catbox.moe/pei3tl.jpg'
        )

        # Now type out the text with the typing effect
        typing_text = (
            "🌴🏝️ <b>Welcome to Island Survival Bot!</b> 🏝️🌴\n\n"
            "You're marooned on a mysterious, untamed island where adventure awaits at every turn! 🌊🐚\n\n"
            "💡 <b>Your Goal:</b> Survive, thrive, and uncover the island's secrets. 🌟\n\n"
            "🌟 Will you explore the dense jungles, brave the wild animals, or uncover hidden treasures?\n\n"
            "🧭 <b>Your journey begins now.</b> Are you ready to face the unknown? Let's get started!"
        )

        # Send the message word by word with a delay
        message_text = ""
        for word in typing_text.split():
            message_text += word + " "
            await sent_message.edit_caption(message_text, parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.3)  # Typing delay

        # Once the text is fully typed, send the "Explore" button
        keyboard = [
            [InlineKeyboardButton("🌿 Explore", callback_data="explore")]
        ]
        await sent_message.reply_text(
            "What will you do next?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

@error_handler_decorator
async def start_adventure(query: CallbackQuery):
    """Handles the start of the adventure with a typing effect."""
    
    # Text to simulate typing effect
    typing_text = [
        "You", "wake", "up", "on", "a", "desolate", "beach,", "the", "remnants", "of", 
        "your", "shipwreck", "scattered", "across", "the", "sand.", "🌊",
        "The", "ocean", "whispers,", "but", "the", "calm", "is", "deceptive—danger", "lurks", 
        "just", "beyond", "the", "shore.", "🌿", "The", "jungle", "calls,", "promising", 
        "resources", "and", "hidden", "secrets,", "but", "also", "unknown", "threats.", "⚔️",
        "Your", "journey", "to", "survive", "begins", "now—gather,", "explore,", "and", 
        "face", "whatever", "challenges", "this", "island", "throws", "your", "way.", "🏹",
        "Are", "you", "ready", "to", "survive?", "🏝️"
    ]

    message = ""

    # Send the message word by word with a delay
    for word in typing_text:
        message += word + " "
        await query.message.edit_text(message, parse_mode=ParseMode.HTML)
        await asyncio.sleep(0.3)  # Typing delay

    # After typing is done, send the image and the Explore button
    keyboard = [
        [InlineKeyboardButton("🌿 Explore", callback_data="explore")]
    ]
    await query.message.reply_photo(
        photo='https://files.catbox.moe/3gbv36.jpg',
        caption="Welcome to your adventure... The island awaits!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@error_handler_decorator
async def show_settings(query: CallbackQuery):
    """Displays settings options (currently just a placeholder)."""
    # Just a basic settings message with no options for now
    await query.message.edit_text(SETTINGS_MESSAGE, parse_mode=ParseMode.HTML)

# Register handlers
def register(app: Client):
    app.add_handler(MessageHandler(start, filters.command("start")))
    app.add_handler(CallbackQueryHandler(start_adventure, filters.regex('^start_adventure$')))
    app.add_handler(CallbackQueryHandler(show_settings, filters.regex('^settings$')))
    app.add_handler(CallbackQueryHandler(explore, filters.regex('^explore$')))  # Add the explore handler
