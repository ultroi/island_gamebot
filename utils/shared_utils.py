import random
import math
from collections import Counter
import json

with open('/workspaces/island_gamebot/data/resources.json') as f:
    resources = json.load(f)

# Experience points required for each level
XP_TABLE = {
    1: 100,
    5: 500,
    10: 1500,
    15: 3000,
    20: 6000,
    30: 12000,
    40: 25000,
    50: 50000
}


def calculate_max_xp(level: int) -> int:
    """Calculate the maximum experience required for the next level based on XP_TABLE."""
    for lvl in sorted(XP_TABLE.keys(), reverse=True):
        if level >= lvl:
            return XP_TABLE[lvl]
    return 100  # Default value if level is below the lowest key in XP_TABLE

def gain_experience(player, xp: int):
    """Add experience points to the player and handle level up if necessary."""
    player.experience += xp
    while player.experience >= player.max_experience:
        player.experience -= player.max_experience
        player.level += 1
        player.max_experience = calculate_max_xp(player.level)
        player.max_health = 100 + (player.level - 1) * 10
        player.max_stamina = 50 + (player.level - 1) * 5
        player.health = player.max_health
        player.stamina = player.max_stamina

def get_health_bar(health: int, max_health: int) -> str:
    health_ratio = health / max_health
    total_blocks = 10  # Length of health bar (total blocks)
    filled_blocks = math.floor(health_ratio * total_blocks)
    
    health_bar = "█" * filled_blocks + "▒" * (total_blocks - filled_blocks)
    return health_bar

def get_stamina_bar(stamina: int, max_stamina: int) -> str:
    stamina_ratio = stamina / max_stamina
    total_blocks = 8  # Length of stamina bar (total blocks)
    filled_blocks = math.floor(stamina_ratio * total_blocks)
    
    # Full stamina bar with positive (yellow) and negative (gray) sections
    stamina_bar = "▮" * filled_blocks + "▯" * (total_blocks - filled_blocks)
    return stamina_bar
    
def get_inventory_capacity(level, area):
    # Base inventory capacity based on level
    if level <= 10:
        base_capacity = 10
    elif level <= 20:
        base_capacity = 15
    elif level <= 30:
        base_capacity = 20
    elif level <= 40:
        base_capacity = 25
    else:
        base_capacity = 30

    # Define the available food and non-food items for the selected area
    food_items_common = resources[area]["food_items"]["common"]
    food_items_rare = resources[area]["food_items"]["rare"]
    non_food_items_common = resources[area]["non_food_items"]["common"]
    non_food_items_rare = resources[area]["non_food_items"]["rare"]

    # Define food and non-food inventory based on the total available slots
    food_inventory = []
    non_food_inventory = []

    # Randomly distribute the total capacity between food and non-food slots
    num_food_items = random.randint(0, base_capacity)  # Random number of food items
    num_non_food_items = base_capacity - num_food_items  # The rest are non-food items

    # Select food items (common and rare)
    food_inventory.extend(random.choices(food_items_common, k=num_food_items // 2))  # Half common
    food_inventory.extend(random.choices(food_items_rare, k=num_food_items // 2))    # Half rare

    # Select non-food items (common and rare)
    non_food_inventory.extend(random.choices(non_food_items_common, k=num_non_food_items // 2))  # Half common
    non_food_inventory.extend(random.choices(non_food_items_rare, k=num_non_food_items // 2))    # Half rare

    # Return the final inventory structure with item slots allocated based on the player's level
    return {
        "total_slots": base_capacity,
        "food_slots": num_food_items,
        "non_food_slots": num_non_food_items,
        "food_inventory": food_inventory,
        "non_food_inventory": non_food_inventory
    }

# Function to calculate remaining space
def get_inventory_space(player):
    # Base capacity based on level
    if player.level <= 10:
        base_capacity = 10
    elif player.level <= 20:
        base_capacity = 15
    elif player.level <= 30:
        base_capacity = 20
    elif player.level <= 40:
        base_capacity = 25
    else:
        base_capacity = 30

    # Calculate space used in inventory
    item_counts = Counter(player.inventory)
    used_space = sum(item_counts.values())  # Total number of items in the inventory

    # Remaining space
    remaining_space = max(0, base_capacity - used_space)

    return used_space, remaining_space, base_capacity