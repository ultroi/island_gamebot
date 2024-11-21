import logging
import traceback
from pyrogram import filters, Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import CallbackQueryHandler
from utils.db_utils import load_player
from collections import Counter
from handlers.error_handler import send_error_to_owner

logger = logging.getLogger(__name__)

async def handle_show_items(client: Client, callback_query: CallbackQuery):
    """Handle inventory display when 'show_items' button is clicked."""
    try:
        user_id = callback_query.from_user.id
        logger.info(f"Handling inventory display for user_id={user_id}")

        # Fetch player data
        player = await load_player(user_id)
        if not player:
            logger.warning(f"No player data found for user_id={user_id}")
            await callback_query.answer("No inventory data found.", show_alert=True)
            return

        # Generate inventory list
        inventory_counts = Counter(item['name'] for item in player.inventory)
        inventory_list = (
            "\n".join(f"<b>{item}:</b> {count}" for item, count in inventory_counts.items())
            or "Your inventory is empty!"
        )

        # Prepare response message
        items_message = f"━━━━━━━━━━━━━━━━━\n<b>Your Inventory:</b>\n{inventory_list}\n━━━━━━━━━━━━━━━━━"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 Back", callback_data="back_to_inventory")]]
        )

        # Edit the message with inventory data
        await callback_query.message.edit_text(
            items_message, reply_markup=keyboard, parse_mode="html"
        )

    except Exception as e:
        # Handle and log exceptions
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Error in handle_show_items: {error_message}", exc_info=True)
        await send_error_to_owner(client, error_message)
        await callback_query.answer("An error occurred. Admin has been notified.", show_alert=True)


async def handle_back_to_inventory(client: Client, callback_query: CallbackQuery):
    """Handle 'back' button to navigate back to inventory."""
    try:
        user_id = callback_query.from_user.id
        logger.info(f"Handling 'back to inventory' for user_id={user_id}")

        # Logic for going back to inventory
        await callback_query.message.edit_text(
            "Back to the main inventory menu.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("View Items", callback_data="show_items")]]
            )
        )

    except Exception as e:
        # Handle and log exceptions
        error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
        logger.error(f"Error in handle_back_to_inventory: {error_message}", exc_info=True)
        await send_error_to_owner(client, error_message)
        await callback_query.answer("An error occurred. Admin has been notified.", show_alert=True)


# Register handlers
def register(app: Client):
    """Register callback query handlers."""
    app.add_handler(CallbackQueryHandler(handle_show_items, filters.regex("^show_items$")))
    app.add_handler(CallbackQueryHandler(handle_back_to_inventory, filters.regex("^back_to_inventory$")))
