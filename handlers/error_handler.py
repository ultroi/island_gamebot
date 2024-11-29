from pyrogram.enums import ParseMode
from pyrogram import Client
from config import OWNER_ID
from pyrogram.types import Message
import logging
import asyncio
import traceback
from functools import wraps

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Custom function to send critical error logs to a specified chat
async def send_error(bot, chat_id: int, message: str):
    """
    Sends a critical error message to a specified chat via Telegram.
    
    Args:
        bot: The Telegram bot instance.
        chat_id: The chat ID to send the message to.
        message: The error message to be sent.
    """
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=f"🚨 <b>Critical Error</b> 🚨\n\n<pre>{message}</pre>",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error(f"Failed to send error to chat {chat_id}: {e}")

class TelegramLogHandler(logging.Handler):
    """
    Custom logging handler to send log messages to the bot owner via Telegram.
    """
    def __init__(self, bot, loop):
        super().__init__()
        self.bot = bot
        self.loop = loop

    def emit(self, record):
        log_entry = self.format(record)
        try:
            # Schedule sending the log entry to the owner
            asyncio.ensure_future(send_error(self.bot, OWNER_ID, log_entry), loop=self.loop)
            # Schedule sending the log entry to the specified chat group
            asyncio.ensure_future(send_error(self.bot, -1002201661092, log_entry), loop=self.loop)
            logger.info(f"Sending log to group: -1002201661092")
        except Exception as e:
            logger.error(f"Error while emitting log entry: {e}")

# Global exception handler for uncaught errors
def global_exception_handler(loop, context):
    app = context.get('app')
    exception = context.get("exception")
    message = context.get("message", "No additional context provided.")
    
    # Log the full exception traceback
    error_message = f"Uncaught Exception:\n\nMessage: {message}"

    if exception:
        error_message += "".join(
            traceback.format_exception(type(exception), exception, exception.__traceback__)
        )
    else:
        error_message += "\n\n(No exception details provided.)"

    # Log the error and send it to the bot owner and the specified chat
    logger.error(error_message, exc_info=exception)
    if app:  # Ensure app is not None
        loop.create_task(send_error(app, OWNER_ID, error_message))
        loop.create_task(send_error(app, -1002201661092, error_message))
    else:
        logger.error("No app instance available to send the error to the owner.")

# Decorator to handle errors in handlers
def error_handler_decorator(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        """
        Wrapper function to handle errors in the decorated handler.
        Logs errors and sends error reports to designated chats.
        """
        try:
            # Execute the decorated function
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            # Generate the detailed traceback for the exception
            error_message = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            logger.error(f"Exception in {func.__name__}: {error_message}")

            # Attempt to send the error message to the owner
            try:
                await send_error(client, OWNER_ID, error_message)
            except Exception as owner_error:
                logger.error(f"Failed to send error to OWNER_ID: {owner_error}")

            # Attempt to send the error message to the group/chat
            try:
                await send_error(client, -1002201661092, error_message)  # Adjust the chat_id if needed
            except Exception as chat_error:
                logger.error(f"Failed to send error to chat -1002201661092: {chat_error}")

            # Optionally re-raise the exception to propagate it further
            raise e

    return wrapper
