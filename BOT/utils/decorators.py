# utils/decorators.py
from functools import wraps
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

# Define a global variable to manage maintenance mode status
MAINTENANCE_MODE = False
developer_id = 5956598856
logging.basicConfig(level=logging.INFO)

def user_verification(func):
    @wraps(func)
    async def wrapped(client: Client, message: Message, *args, **kwargs):
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Check if the current user is the authorized user for this interaction
        if message:
            # Command initiation
            client.storage[chat_id]["authorized_user_id"] = user_id
        elif isinstance(message, CallbackQuery):
            # Button interaction
            authorized_user_id = client.storage[chat_id].get("authorized_user_id")
            if user_id != authorized_user_id:
                # Send alert to unauthorized users trying to press a button
                await message.answer("🚫 You are not authorized to interact with this button.", show_alert=True)
                return  # Exit if user is not authorized

        # Proceed if authorized or if it's a new command initiation
        return await func(client, message, *args, **kwargs)
    return wrapped

def maintenance_mode_only(func):
    @wraps(func)
    async def wrapped(client: Client, message: Message, *args, **kwargs):
        global MAINTENANCE_MODE
        user_id = message.from_user.id

        if message:
            logging.info(f"Received command: {message.text} from user: {user_id}")

        try:
            # Check if the update is a message and has text
            if message and message.text:
                command_text = message.text.strip()  # Normalize the command
                logging.info(f"Command text: {command_text}")

                # Enable maintenance mode
                if command_text == "/mmode" and user_id == developer_id:
                    logging.info("Activating maintenance mode")
                    MAINTENANCE_MODE = True
                    await message.reply("🏝️ Maintenance mode activated! The island is getting a makeover. Please stand by...")
                    logging.info(f"Maintenance mode activated by user ID: {user_id}")
                    return

                # Disable maintenance mode
                elif command_text == "/dmmode" and user_id == developer_id:
                    logging.info("Deactivating maintenance mode")
                    MAINTENANCE_MODE = False
                    await message.reply("🏝️ Maintenance mode lifted! The island is ready for your next adventure!")
                    logging.info(f"Maintenance mode deactivated by user ID: {user_id}")
                    return

            # If maintenance mode is active and user is not the developer
            if MAINTENANCE_MODE:
                if user_id == developer_id:
                    # Allow developer to bypass maintenance mode
                    logging.info(f"Developer bypassed maintenance mode: {user_id}")
                    return await func(client, message, *args, **kwargs)
                else:
                    # Notify unauthorized users about maintenance
                    if message:
                        await message.reply("🚧 The island is currently closed for repairs. Please return later!")
                    elif isinstance(message, CallbackQuery):
                        await message.answer("🚧 The island is currently closed for repairs. Please return later!", show_alert=True)
                    logging.info(f"Unauthorized user attempted access during maintenance: {user_id}")
                    return  # No reaction for unauthorized users in maintenance mode

            # If the developer is using the command or maintenance mode is off, execute the command
            return await func(client, message, *args, **kwargs)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            # Handle any exceptions that occur during the execution
            if message:
                await message.reply(f"An error occurred: {e}")
            elif isinstance(message, CallbackQuery):
                await message.answer(f"An error occurred: {e}", show_alert=True)
            raise e  # Re-raise the exception to ensure it's not silently ignored

    return wrapped