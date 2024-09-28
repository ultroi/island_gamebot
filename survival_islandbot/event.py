import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import add_event, update_resources, get_resources

def explore_forest(player_id):
    events = [
        "You found a treasure chest!",
        "You encountered a wild animal!",
        "You met another survivor!",
        "You found some berries to eat!",
        "You stumbled upon an abandoned campsite!",
        "You found a magical artifact!"
    ]
    random_event = random.choice(events)
    
    # Log the event in the database
    add_event(player_id, "exploration", random_event)

    if "wild animal" in random_event:
        return dangerous_animal_event(player_id)
    elif "treasure chest" in random_event:
        return treasure_chest_event(player_id)
    elif "survivor" in random_event:
        return survivor_event(player_id)
    elif "berries" in random_event:
        return berry_event(player_id)
    elif "campsite" in random_event:
        return campsite_event(player_id)
    elif "artifact" in random_event:
        return artifact_event(player_id)

    return random_event

def dangerous_animal_event(player_id):
    keyboard = [
        [InlineKeyboardButton("Fight", callback_data='fight')],
        [InlineKeyboardButton("Flee", callback_data='flee')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    return "You encounter a dangerous animal! What do you want to do?", reply_markup

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    choice = query.data
    player_id = context.user_data['player_id']
    
    if choice == 'fight':
        result = dangerous_animal_event_fight(player_id)  # Implement this logic
    elif choice == 'flee':
        result = "You managed to escape safely!"
    
    query.edit_message_text(text=result)

def dangerous_animal_event_fight(player_id):
    # Placeholder for combat logic (can be expanded)
    if random.choice([True, False]):  # Random chance of winning
        # Assuming player gets some resources or XP for winning
        update_resources(player_id, 0, 0, 1)  # Reward: +1 water
        return "You fought bravely and defeated the animal! You found 1 water."
    else:
        return "You were injured in the fight! Lose 10 health points."

# Other event functions...

