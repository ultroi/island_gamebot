from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from shared import get_player, update_player


async def craft(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)

    if player:
        resources = player[4].split(", ") if player[4] else []
        if "wood" in resources and "stone" in resources:
            update_player(user_id, "resources", "")
            update_player(user_id, "inventory", player[3] + ", crafted_weapon")
            await update.message.reply_text("You crafted a stone weapon!")
        else:
            await update.message.reply_text("You don't have enough resources to craft anything.")
    else:
        await update.message.reply_text("You need to start the game with /start first.")
    context.chat_data  # Access chat data to ensure context is used


def get_building_quality(inventory):
    items = inventory.split(", ") if inventory else []
    
    # Count items in inventory
    item_counts = {item: items.count(item) for item in set(items)}
    wood = item_counts.get("wood", 0)
    leaves = item_counts.get("leaves", 0)
    stones = item_counts.get("stone", 0)

    # Required materials for each quality
    requirements = {
        "Low Grade": {"wood": 3},
        "+ Grade": {"wood": 3, "leaves": 2},
        "++ Grade": {"wood": 3, "stone": 2},
        "+++ Grade": {"wood": 3, "stone": 2, "leaves": 2}
    }

    # Check which grade can be built and how many materials are still needed
    possible_grades = {}
    
    for grade, req in requirements.items():
        missing = {item: req[item] - item_counts.get(item, 0) for item in req}
        if all(v <= 0 for v in missing.values()):  # If no missing materials
            possible_grades[grade] = {"status": "Can build", "missing": {}}
        else:
            possible_grades[grade] = {"status": "Missing materials", "missing": missing}

    return possible_grades, item_counts  # Return possible shelter grades and current inventory count


async def build(update: Update, context: CallbackContext.DEFAULT_TYPE):
    user_id = update.effective_user.id
    player = get_player(user_id)

    if player:
        inventory = player[3]
        # Determine the building quality based on available materials
        possible_grades, item_counts = get_building_quality(inventory)

        build_message = "🏠 **Build Shelter** 🏠\n\n"
        build_options = []

        # Show each possible shelter grade and required/missing materials
        for grade, status_info in possible_grades.items():
            status = status_info['status']
            missing_text = ""
            if status == "Missing materials":
                missing_text = " (Need more: " + ", ".join(
                    f"{item} ({abs(count)} more)" for item, count in status_info['missing'].items()
                ) + ")"
            
            build_message += f"{grade}: {status}{missing_text}\n"
            
            # If buildable, add to interactive options
            if status == "Can build":
                build_options.append([InlineKeyboardButton(f"Build {grade}", callback_data=f"build_{grade.replace(' ', '_').lower()}")])

        # Check if there are any build options available
        if build_options:
            await update.message.reply_text(
                build_message + "\nChoose the shelter quality to build:",
                reply_markup=InlineKeyboardMarkup(build_options)
            )
        else:
            await update.message.reply_text(build_message + "\nYou don't have enough materials to build any shelter.")
    else:
        await update.message.reply_text("You need to start the game with /start first.")
    context.chat_data  # Access chat data to ensure context is used


async def handle_build_shelter(update: Update, context: CallbackContext.DEFAULT_TYPE):
    query = update.callback_query
    quality = query.data.split("_")[1].replace("_", " ")
    user_id = query.from_user.id
    player = get_player(user_id)

    # Deduct materials based on the building quality
    if quality == "low_grade":
        update_inventory(user_id, "wood", remove=True, count=3)
    elif quality == "grade":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "leaves", remove=True, count=2)
    elif quality == "wood_stone":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "stone", remove=True, count=2)
    elif quality == "wood_stone_leaves":
        update_inventory(user_id, "wood", remove=True, count=3)
        update_inventory(user_id, "stone", remove=True, count=2)
        update_inventory(user_id, "leaves", remove=True, count=2)

    await query.message.edit_text(f"You have successfully built a **{quality.replace('_', ' ')}** shelter!")

    context.chat_data  # Access chat data to ensure context is used


def update_inventory(user_id, item, remove=False, count=1):
    player = get_player(user_id)
    items = player[3].split(", ") if player[3] else []

    if remove:
        for _ in range(count):
            if item in items:
                items.remove(item)
    else:
        items.extend([item] * count)

    # Update the player's inventory in the database
    new_inventory = ", ".join(items)
    update_player(user_id, "inventory", new_inventory)


def has_shelter_in_location(player):
    current_location = player[5]  # Player's current location
    shelter_status = player[6]    # Player's shelter status (story_progress could be used for this)
    
    return f"shelter_{current_location}" in shelter_status


