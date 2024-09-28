import random
from database import get_player_stats, update_player_health, get_player_weapon, get_enemy_stats
from utils import notify_player, create_inline_button

def health_bar(current_health, max_health):
    """
    Creates a visual representation of health using bars.
    
    :param current_health: The current health of the entity
    :param max_health: The maximum health of the entity
    :return: A string representing the health bar
    """
    bar_length = 20  # Total number of characters in the bar
    health_ratio = current_health / max_health
    filled_length = int(bar_length * health_ratio)
    
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    return f"{current_health}/{max_health} [{bar}]"

def engage_combat(player_id, enemy_name):
    """
    Engages the player in combat with an enemy or animal and displays health status.
    
    :param player_id: ID of the player
    :param enemy_name: The enemy the player is fighting
    :return: Result of the combat encounter
    """
    player_stats = get_player_stats(player_id)
    enemy_stats = get_enemy_stats(enemy_name)
    
    player_health = player_stats["health"]
    player_strength = player_stats["strength"]
    player_weapon = get_player_weapon(player_id)
    
    enemy_health = enemy_stats["health"]
    enemy_damage = enemy_stats["damage"]
    
    max_player_health = player_stats["max_health"]
    max_enemy_health = enemy_stats["max_health"]
    
    # Combat loop
    while player_health > 0 and enemy_health > 0:
        # Player attacks enemy
        weapon_damage = player_weapon.get("damage", 1)  # Default to 1 if no weapon is equipped
        total_damage_to_enemy = player_strength + weapon_damage
        enemy_health -= total_damage_to_enemy
        
        # Display player attacking the enemy
        notify_player(player_id, f"You attack the {enemy_name} and deal {total_damage_to_enemy} damage.")
        
        # Display current health status
        notify_player(player_id, f"Your health: {health_bar(player_health, max_player_health)}")
        notify_player(player_id, f"{enemy_name}'s health: {health_bar(enemy_health, max_enemy_health)}")

        # Check if enemy is defeated
        if enemy_health <= 0:
            notify_player(player_id, f"Victory! You defeated the {enemy_name}!")
            return f"Victory! You defeated the {enemy_name}."

        # Enemy attacks player
        total_damage_to_player = enemy_damage
        player_health -= total_damage_to_player
        
        # Display enemy attacking the player
        notify_player(player_id, f"The {enemy_name} attacks you and deals {total_damage_to_player} damage.")

        # Display updated health status after enemy attack
        notify_player(player_id, f"Your health: {health_bar(player_health, max_player_health)}")
        notify_player(player_id, f"{enemy_name}'s health: {health_bar(enemy_health, max_enemy_health)}")
        
        # Check if player is defeated
        if player_health <= 0:
            update_player_health(player_id, 0)
            return f"You were defeated by the {enemy_name}. Game over."
        
        # Provide inline buttons for the player to continue fighting or flee
        buttons = [
            create_inline_button("Fight", callback_data=f"fight_{enemy_name}"),
            create_inline_button("Flee", callback_data=f"flee_{enemy_name}")
        ]
        notify_player(player_id, "What do you want to do?", buttons=buttons)
        break  # Break loop here, next action will be triggered based on button click

    # Update player's health after combat round
    update_player_health(player_id, player_health)
    return f"Combat ended. Your remaining health: {player_health}"

def attack(player_id, enemy_name):
    """
    Initiates an attack on an enemy.
    
    :param player_id: ID of the player
    :param enemy_name: Name of the enemy to attack
    """
    combat_result = engage_combat(player_id, enemy_name)
    notify_player(player_id, combat_result)

def flee(player_id, enemy_name):
    """
    Allows the player to flee from combat with a random chance of success.
    
    :param player_id: ID of the player
    :param enemy_name: Name of the enemy they are fleeing from
    :return: Result of the flee attempt
    """
    flee_success = random.choice([True, False])
    
    if flee_success:
        notify_player(player_id, f"You successfully fled from the {enemy_name}.")
        return f"You successfully fled from the {enemy_name}."
    else:
        return engage_combat(player_id, enemy_name)  # Continue combat if fleeing fails
