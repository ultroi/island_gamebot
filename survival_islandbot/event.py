import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import add_event, update_resources, get_resources
from utils import notify_player  # Assuming you have a utility to send notifications

def explore_forest(player_id):
    """
    Allows the player to explore the forest and encounter random events.
    
    :param player_id: ID of the player exploring
    :return: Message indicating exploration outcome
    """
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
    """
    Handles the event where the player encounters a dangerous animal.
    
    :param player_id: ID of the player encountering the animal
    :return: Tuple containing the event message and inline keyboard markup
    """
    keyboard = [
        [InlineKeyboardButton("Fight", callback_data='fight')],
        [InlineKeyboardButton("Flee", callback_data='flee')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    return "You encounter a dangerous animal! What do you want to do?", reply_markup

def button_callback(update: Update, context: CallbackContext):
    """
    Handles button callbacks for animal encounters.
    
    :param update: Update object containing the callback query
    :param context: CallbackContext containing data related to the callback
    """
    query = update.callback_query
    query.answer()
    
    choice = query.data
    player_id = context.user_data['player_id']
    
    if choice == 'fight':
        result = dangerous_animal_event_fight(player_id)  # Call the combat logic
    elif choice == 'flee':
        result = "You managed to escape safely!"
    
    query.edit_message_text(text=result)

def dangerous_animal_event_fight(player_id):
    """
    Handles the logic for fighting a dangerous animal.
    
    :param player_id: ID of the player fighting the animal
    :return: Result message of the encounter
    """
    # Placeholder for combat logic
    if random.choice([True, False]):  # Random chance of winning
        # Assuming player gets some resources or XP for winning
        update_resources(player_id, 0, 0, 1)  # Reward: +1 water
        return "You fought bravely and defeated the animal! You found 1 water."
    else:
        return "You were injured in the fight! Lose 10 health points."

def treasure_chest_event(player_id):
    """Handles the event when the player finds a treasure chest."""
    # Logic for opening a treasure chest
    # Example: Update player resources, notify the player, etc.
    resources_found = {"wood": 5, "berries": 3}  # Example resources
    for res_type, amount in resources_found.items():
        update_resources(player_id, amount)  # Add resources
    notify_player(player_id, f"You opened a treasure chest and found: {resources_found}!")

def survivor_event(player_id):
    """Handles the event when the player meets another survivor."""
    # Logic for interacting with another survivor
    notify_player(player_id, "You met another survivor! They offer you some advice and a few supplies.")

def berry_event(player_id):
    """Handles the event when the player finds berries."""
    # Logic for finding berries
    update_resources(player_id, 0, 0, 5)  # Add berries to resources
    notify_player(player_id, "You found some berries to eat! +5 Berries.")

def campsite_event(player_id):
    """Handles the event when the player stumbles upon an abandoned campsite."""
    # Logic for the abandoned campsite
    notify_player(player_id, "You stumbled upon an abandoned campsite. It looks like it hasn't been used in a while.")

def artifact_event(player_id):
    """Handles the event when the player finds a magical artifact."""
    # Logic for finding a magical artifact
    notify_player(player_id, "You found a magical artifact! Its purpose is unknown, but it feels powerful.")

# Define other event functions as needed...
