from functools import wraps
import logging
from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from utils.db_utils import load_player

# Define a global variable to manage maintenance mode status
MAINTENANCE_MODE = False
developer_id = 5956598856
logging.basicConfig(level=logging.INFO)

# def user_verification(func):
#     """Decorator to verify if a user is authorized to execute a command or interact with buttons."""
#     @wraps(func)
#     async def wrapped(client: Client, *args, **kwargs):
#         update = args[0] if args else kwargs.get('update', None)
#         user_id = update.from_user.id if isinstance(update, (Message, CallbackQuery)) else None

#         if user_id is None:
#             return  # No user to verify

#         # Fetch player data (which includes authorized user info)
#         player = await load_player(user_id)

#         if player is None:
#             # Player not found; possibly not registered
#             if isinstance(update, CallbackQuery):
#                 await update.answer("🚫 Player data not found. Please register first.", show_alert=True)
#             elif isinstance(update, Message):
#                 await update.reply("🚫 Player data not found. Please register first.")
#             return

#         # Check if the current user is the authorized user for button interactions
#         if isinstance(update, CallbackQuery):
#             command_initiator_id = update.message.reply_to_message.from_user.id if update.message.reply_to_message else None
#             if user_id != command_initiator_id:
#                 await update.answer("🚫 You are not authorized to interact with this button.", show_alert=True)
#                 return

#         # Proceed if the user is authorized or it's a command message
#         return await func(client, *args, **kwargs)

#     return wrapped

def maintenance_mode_only(*args, **kwargs):
    func = args[0]
    @wraps(func)
    async def wrapped(client: Client, *args, **kwargs):
        global MAINTENANCE_MODE
        update = args[0] if args else kwargs.get('update', None)
        user_id = update.from_user.id if isinstance(update, (Message, CallbackQuery)) else None

        if isinstance(update, Message):
            logging.info(f"Received command: {update.text} from user: {user_id}")

        try:
            # Check if the update is a message and has text
            if isinstance(update, Message) and update.text:
                command_text = update.text.strip()  # Normalize the command
                logging.info(f"Command text: {command_text}")

                # Enable maintenance mode
                if command_text == "/mmode" and user_id == developer_id:
                    logging.info("Activating maintenance mode")
                    MAINTENANCE_MODE = True
                    await update.reply("🏝️ Maintenance mode activated! The island is getting a makeover. Please stand by...")
                    logging.info(f"Maintenance mode activated by user ID: {user_id}")
                    return

                # Disable maintenance mode
                elif command_text == "/dmmode" and user_id == developer_id:
                    logging.info("Deactivating maintenance mode")
                    MAINTENANCE_MODE = False
                    await update.reply("🏝️ Maintenance mode lifted! The island is ready for your next adventure!")
                    logging.info(f"Maintenance mode deactivated by user ID: {user_id}")
                    return

            # If maintenance mode is active and user is not the developer
            if MAINTENANCE_MODE:
                if user_id == developer_id:
                    # Allow developer to bypass maintenance mode
                    logging.info(f"Developer bypassed maintenance mode: {user_id}")
                    return await func(client, *args, **kwargs)
                else:
                    # Notify unauthorized users about maintenance
                    if isinstance(update, Message):
                        await update.reply("🚧 The island is currently closed for repairs. Please return later!")
                    elif isinstance(update, CallbackQuery):
                        await update.answer("🚧 The island is currently closed for repairs. Please return later!", show_alert=True)
                    logging.info(f"Unauthorized user attempted access during maintenance: {user_id}")
                    return  # No reaction for unauthorized users in maintenance mode

            # If the developer is using the command or maintenance mode is off, execute the command
            return await func(client, *args, **kwargs)

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            # Handle any exceptions that occur during the execution
            if isinstance(update, Message):
                await update.reply(f"An error occurred: {e}")
            elif isinstance(update, CallbackQuery):
                await update.answer(f"An error occurred: {e}", show_alert=True)
            raise e  # Re-raise the exception to ensure it's not silently ignored

    return wrapped
