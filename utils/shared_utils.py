import math
import json
import logging
import os

with open('/workspaces/island_gamebot/data/config.json') as f:
    resources = json.load(f)

def load_config():
    config_path = "/workspaces/island_gamebot/data/config.json"
    if not os.path.exists(config_path):
        logging.error(f"Configuration file {config_path} not found.")
        return {}
    try:
        with open(config_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error("Configuration file is not a valid JSON.")
        return {}


# Function to calculate the max XP based on level difference (using developer config or default)
def calculate_max_xp(current_level: int, next_level: int) -> int:
    """
    Calculate the XP required to level up based on the difference between levels.
    Uses developer's configuration or default calculation.
    """
    config = load_config()

    # Get the XP increment per level from the developer's configuration
    xp_increment_per_level = config.get("level_requirements", {}).get("xp_per_level")
    # Get the XP multiplier for level-ups (if configured)
    xp_multiplier = config.get("xp_gain", {}).get("level_multiplier")


    if xp_increment_per_level is None:
        logging.error("XP increment per level is not defined in the configuration.", exc_info=True)
        return 0
    # Calculate the level difference
    level_difference = next_level - current_level
    if level_difference <= 0:
        logging.error(f"Invalid level difference: {next_level} must be greater than {current_level}.")
        return 0  # Return 0 if level difference is invalid

    # Calculate the base XP for this level-up difference
    base_xp_required = xp_increment_per_level * level_difference

    # Apply the XP multiplier if set in the config
    max_xp = base_xp_required * xp_multiplier
    logging.info(f"XP required for leveling up from level {current_level} to level {next_level}: {max_xp}")
    return max_xp

# Calculate XP based on the config
def calculate_xp(player, config):
    base_xp = config['xp_gain']['per_item']
    level_multiplier = config['xp_gain']['level_multiplier']
    return base_xp + (level_multiplier ** (player.level - 1))

# Function to calculate the total XP required to reach the next level from level 1
def get_level_xp(current_level: int) -> int:
    """Calculate the total XP required to reach the next level from level 1."""
    total_xp = 0
    for level in range(1, current_level + 1):
        total_xp += calculate_max_xp(level, level + 1)
    return total_xp

def gain_experience(player, xp: int):
    """Add experience points to the player and handle level up if necessary."""
    player.experience += xp
    while player.experience >= player.max_experience:
        player.experience -= player.max_experience
        player.level += 1
        player.max_experience = calculate_max_xp(player.level)
        player.max_health = get_max_health(player.level, load_config())
        player.max_stamina = get_max_stamina(player.level, load_config())
        player.health = player.max_health
        player.stamina = player.max_stamina

# Get max health based on player level
def get_max_health(level, config):
    base_health = config['max_health']['base']
    health_per_level = config['max_health']['per_level']
    return base_health + (level - 1) * health_per_level

def get_max_stamina(level, config):
    base_stamina = config['max_stamina']['base']
    stamina_per_level = config['max_stamina']['per_level']
    return base_stamina + (level - 1) * stamina_per_level

def get_health_bar(health: int, max_health: int) -> str:
    health_ratio = health / max_health
    total_blocks = 10  # Length of health bar (total blocks)
    filled_blocks = math.floor(health_ratio * total_blocks)
    
    health_bar = "█" * filled_blocks + "▒" * (total_blocks - filled_blocks)
    return health_bar

def get_stamina_bar(stamina: int, max_stamina: int) -> str:
    stamina_ratio = stamina / max_stamina
    total_blocks = 7  # Length of stamina bar (total blocks)
    filled_blocks = math.floor(stamina_ratio * total_blocks)
    
    # Full stamina bar with positive (yellow) and negative (gray) sections
    stamina_bar = "▮" * filled_blocks + "▯" * (total_blocks - filled_blocks)
    return stamina_bar
