from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ParseMode
from utils.db_utils import load_player
from collections import Counter
from utils.decorators import user_verification, maintenance_mode_only
from utils.shared_utils import get_health_bar, get_stamina_bar, get_inventory_space
import json

with open('/workspaces/island_gamebot/data/resources.json') as f:
    resources = json.load(f)


# Show inventory for the player
async def show_inventory(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    player = await load_player(user_id)
    
    if player is None:
        await query.message.reply("Player not found. Please register first.")
        return

    # Generate health and stamina bars
    health_bar = get_health_bar(player.health, player.max_health)
    stamina_bar = get_stamina_bar(player.stamina, player.max_stamina)
    used_space, remaining_space, total_space = get_inventory_space(player)
    inventory_list = "\n".join(player.inventory)

    inventory_message = (
        f"┣👤 <b>Name</b>: {player.name}\n"
        f"┣❤️ <b>HP</b>: {player.health}/{player.max_health}\n"
        f"┣🔹 <b>Health Bar</b>: {health_bar}\n\n"
        f"┣⚡ <b>Stamina</b>: {player.stamina}/{player.max_stamina}\n"
        f"┣🔹 <b>Stamina Bar</b>: {stamina_bar}\n\n"
        f"┣📍 <b>Current Location</b>: {player.location}\n\n"
        f"┏━━━━━━━━━━━━━━━━\n"
        f"┣ 📦 <b>Inventory</b>:\n{inventory_list}\n\n"
        f"┗━━━━━━━━━━━━━━━━\n\n"
        f"┣🏆 <b>Level</b>: {player.level}\n"
        f"┣💎 <b>XP</b>: {player.experience}/{player.max_experience}\n"
        f"┣🛠️ <b>Remaining Space</b>: {remaining_space}/{total_space}\n\n"
        f"┗━━━━━━━━━━━━━━━━\n\n"
    )

    await query.message.edit_text(inventory_message, parse_mode="HTML")


# Register function to allow integration in main.py
def register(app: Client):
    app.add_handler(Client.on_callback_query(filters.create(maintenance_mode_only) & filters.create(user_verification))(show_inventory))
