# utils/inventory_utils.py
from typing import List
import json

# Load the dev config for exploration
with open('/workspaces/island_gamebot/data/config.json') as f:
    config = json.load(f)

with open('/workspaces/island_gamebot/data/items.json') as f:
    items_config = json.load(f)

    def get_inventory_capacity(player, location: str, config: dict, items_config: List[dict]) -> int:
        # Calculate base capacity from player's inventory
        base_capacity = 0
        for item in player.inventory:
            item_type = item.get("type", "common")
            # Retrieve space usage per item type
            space_per_item = config["space_per_item"].get(item_type, 1)  # Default to 1 if type not found
            base_capacity += space_per_item
        
        # Additional capacity from player's level
        level_multiplier = config["level_requirements"].get("xp_per_level", 100)
        xp_per_level = config["level_requirements"].get("xp_per_level", 100)
        xp_increment_per_level = config["level_requirements"].get("xp_increment_per_level", 10)
    
        # Calculate capacity based on player's level
        level_capacity = player.level * xp_per_level + (xp_increment_per_level * player.level)
    
        # Ensure location is a string
        if isinstance(location, str):
            # Location-based bonus (example: the "beach" location does not add a bonus)
            location_bonus = 0 if location.lower() == "beach" else 2
        else:
            location_bonus = 0
    
        # Final capacity calculation
        total_capacity = base_capacity + level_capacity + location_bonus
        return total_capacity
