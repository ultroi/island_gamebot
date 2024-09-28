import random
from database import update_resources, get_resources
from utils import notify_player
from combat import engage_combat

def explore_area(player_id, area_name):
    """
    Allows the player to explore a specified area and encounter random events.

    :param player_id: ID of the player
    :param area_name: Name of the area to explore (e.g., 'forest', 'beach')
    :return: Exploration result
    """
    events = {
        "forest": ["You found wood!", "You encountered a wolf!", "You found berries!"],
        "beach": ["You found shells!", "You encountered a crab!", "You found fish!"],
    }
    
    random_event = random.choice(events.get(area_name, []))
    
    if "encountered" in random_event:
        enemy = random_event.split(" ")[2].strip("!")
        return engage_combat(player_id, enemy)
    else:
        return handle_resource_event(player_id, random_event)

def handle_resource_event(player_id, event):
    """
    Handles resource-gathering events during exploration.
    
    :param player_id: ID of the player
    :param event: The resource event string
    :return: Message about the gathered resources
    """
    resources = {
        "wood": (1, 5),
        "berries": (1, 3),
        "fish": (1, 4),
        "shells": (1, 2),
    }
    
    for resource, range_values in resources.items():
        if resource in event:
            amount = random.randint(*range_values)
            update_resources(player_id, {resource: amount})
            return f"You gathered {amount} {resource}."

    return "You explored but didn't find anything useful."
