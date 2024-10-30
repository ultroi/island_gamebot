# utils/decorators.py
from functools import wraps
import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

# Define a global variable to manage maintenance mode status
MAINTENANCE_MODE = False
developer_id = 5956598856
logging.basicConfig(level=logging.INFO)

def user_verification(func):
    @wraps(func)
    async def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Check if the current user is the authorized user for this interaction
        if update.message:
            # Command initiation
            context.chat_data["authorized_user_id"] = user_id
        elif update.callback_query:
            # Button interaction
            authorized_user_id = context.chat_data.get("authorized_user_id")
            if user_id != authorized_user_id:
                # Send alert to unauthorized users trying to press a button
                await update.callback_query.answer("🚫 You are not authorized to interact with this button.", show_alert=True)
                return  # Exit if user is not authorized

        # Proceed if authorized or if it's a new command initiation
        return await func(update, context, *args, **kwargs)
    return wrapped

def maintenance_mode_only(func):
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        global MAINTENANCE_MODE
        user_id = update.effective_user.id

        if update.message:
            logging.info(f"Received command: {update.message.text} from user: {user_id}")

        try:
            # Check if the update is a message and has text
            if update.message and update.message.text:
                command_text = update.message.text.strip()  # Normalize the command
                logging.info(f"Command text: {command_text}")

                # Enable maintenance mode
                if command_text == "/mmode" and user_id == developer_id:
                    logging.info("Activating maintenance mode")
                    MAINTENANCE_MODE = True
                    await update.message.reply_text("🏝️ Maintenance mode activated! The island is getting a makeover. Please stand by...")
                    logging.info(f"Maintenance mode activated by user ID: {user_id}")
                    return

                # Disable maintenance mode
                elif command_text == "/dmmode" and user_id == developer_id:
                    logging.info("Deactivating maintenance mode")
                    MAINTENANCE_MODE = False
                    await update.message.reply_text("🏝️ Maintenance mode lifted! The island is ready for your next adventure!")
                    logging.info(f"Maintenance mode deactivated by user ID: {user_id}")
                    return

            # If maintenance mode is active and user is not the developer
            if MAINTENANCE_MODE:
                if user_id == developer_id:
                    # Allow developer to bypass maintenance mode
                    logging.info(f"Developer bypassed maintenance mode: {user_id}")
                    return await func(update, context, *args, **kwargs)
                else:
                    # Notify unauthorized users about maintenance
                    if update.message:
                        await update.message.reply_text("🚧 The island is currently closed for repairs. Please return later!")
                    elif update.callback_query:
                        await update.callback_query.answer("🚧 The island is currently closed for repairs. Please return later!", show_alert=True)
                    logging.info(f"Unauthorized user attempted access during maintenance: {user_id}")
                    return  # No reaction for unauthorized users in maintenance mode

            # If the developer is using the command or maintenance mode is off, execute the command
            return await func(update, context, *args, **kwargs)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            # Handle any exceptions that occur during the execution
            if update.message:
                await update.message.reply_text(f"An error occurred: {e}")
            elif update.callback_query:
                await update.callback_query.answer(f"An error occurred: {e}", show_alert=True)
            raise e  # Re-raise the exception to ensure it's not silently ignored

    return wrapped