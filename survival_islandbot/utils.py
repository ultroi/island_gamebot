from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.error import TelegramError
import logging

logging.basicConfig(level=logging.INFO)

def send_message_with_buttons(bot: Bot, player_id: int, text: str, items: list) -> None:
    """
    Sends a message to the player with inline buttons for the given items.

    :param bot: The bot instance to use for sending messages
    :param player_id: ID of the player to send the message to
    :param text: The message text
    :param items: List of items for which to create buttons
    """
    buttons = [[InlineKeyboardButton(item, callback_data=f"craft_{item}")] for item in items]
    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        bot.send_message(chat_id=player_id, text=text, reply_markup=reply_markup)
        logging.info(f"Sent message with buttons to player {player_id}")
    except TelegramError as e:
        logging.error(f"Failed to send message to player {player_id}: {e}")

def notify_player(bot: Bot, player_id: int, message: str) -> None:
    """
    Simple helper function to send a notification to the player.

    :param bot: The bot instance to use for sending messages
    :param player_id: ID of the player to notify
    :param message: The message to send
    """
    try:
        bot.send_message(chat_id=player_id, text=message)
        logging.info(f"Sent notification to player {player_id}")
    except TelegramError as e:
        logging.error(f"Failed to notify player {player_id}: {e}")
