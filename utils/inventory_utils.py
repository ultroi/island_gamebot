# utils/inventory_utils.py
from typing import List
import json

# Load the dev config for exploration
with open('/workspaces/island_gamebot/data/config.json') as f:
    config = json.load(f)

with open('/workspaces/island_gamebot/data/items.json') as f:
    items_config = json.load(f)

def get_inventory_capacity(player, location: str, config: dict, items_config: List[dict]) -> int:
    """
    Calculate the inventory capacity based on player's level, items in inventory, and location.
    
    Args:
        player: The player object.
        location: The current location of the player.
        config: The configuration dictionary (from config.json).
        items_config: The list of items (from items.json).
    
    Returns:
        int: The total inventory capacity.
    """
    # Calculate base capacity from player's inventory
    base_capacity = 0
    for item in player.inventory:
        item_type = item.get("type", "common")
        space_per_item = config["space_per_item"].get(item_type, 1)  # Default to 1 if type not found
        base_capacity += space_per_item

    # Additional capacity from player's level
    level_multiplier = config["level_requirements"].get("xp_per_level", 100)

    # Location-specific bonus
    location_bonus = 0 if location.lower() == "beach" else 2

    # Final capacity calculation
    return base_capacity + (player.level * level_multiplier) + location_bonus
