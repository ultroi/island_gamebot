from pyrogram.enums import ParseMode
from client import app
import logging
import asyncio
import traceback

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Bot Owner ID
OWNER_ID = 5956598856

# Custom log handler to send critical errors to the owner
async def send_error_to_owner(bot, message: str):
    try:
        await bot.send_message(
            chat_id=OWNER_ID,
            text=f"🚨 *Critical Error* 🚨\n\n```\n{message}\n```",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to send error to owner: {e}")

class TelegramLogHandler(logging.Handler):
    """Custom log handler to send logs to the Telegram bot owner."""
    def __init__(self, bot, loop):
        super().__init__()
        self.bot = bot
        self.loop = loop

    def emit(self, record):
        log_entry = self.format(record)
        asyncio.run_coroutine_threadsafe(
            send_error_to_owner(self.bot, log_entry), self.loop
        )

# Global exception handler for uncaught errors
def global_exception_handler(loop, context):
    exception = context.get("exception")
    logger.error("Uncaught exception", exc_info=exception)
    if exception:
        # Send exception to the owner asynchronously
        loop.create_task(
            send_error_to_owner(
                app,
                "".join(
                    traceback.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                ),
            )
        )