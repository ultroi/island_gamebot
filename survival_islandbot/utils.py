from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def send_message_with_buttons(player_id, text, items):
    """
    Sends a message to the player with inline buttons for the given items.

    :param player_id: ID of the player to send the message to
    :param text: The message text
    :param items: List of items for which to create buttons
    """
    # Create inline keyboard buttons
    buttons = [[InlineKeyboardButton(item, callback_data=f"craft_{item}")] for item in items]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Send message with inline buttons
    bot.send_message(chat_id=player_id, text=text, reply_markup=reply_markup)

def notify_player(player_id, message):
    """
    Simple helper function to send a notification to the player.

    :param player_id: ID of the player to notify
    :param message: The message to send
    """
    bot.send_message(chat_id=player_id, text=message)
