import random
from database import update_resources, get_resources

def gather_resources(player_id):
    # Simulate gathering resources
    wood = random.randint(1, 5)
    food = random.randint(1, 5)
    water = random.randint(1, 3)

    # Update the database
    update_resources(player_id, wood, food, water)
    
    return f"You gathered: {wood} wood, {food} food, {water} water."


def craft_weapon(player_id, weapon_type):
    resources = get_resources(player_id)
    
    if weapon_type == "spear":
        required_wood = 3
        if resources[0] >= required_wood:
            # Update resources after crafting
            update_resources(player_id, -required_wood, 0, 0)
            return "You crafted a spear!"
        else:
            return "Not enough wood to craft a spear."
    else:
        return "Unknown weapon type."


def build_shelter(player_id, shelter_type):
    resources = get_resources(player_id)

    if shelter_type == "small":
        required_wood = 5
        if resources[0] >= required_wood:
            # Deduct wood and upgrade shelter level
            update_resources(player_id, -required_wood, 0, 0)
            return "You built a small shelter!"
        else:
            return "Not enough wood to build a small shelter."
    elif shelter_type == "medium":
        required_wood = 10
        if resources[0] >= required_wood:
            update_resources(player_id, -required_wood, 0, 0)
            return "You built a medium shelter!"
        else:
            return "Not enough wood to build a medium shelter."
    else:
        return "Unknown shelter type."


def explore_forest(player_id):
    events = [
        "You found a treasure chest!",
        "You encountered a wild animal!",
        "You met another survivor!",
        "You found some berries to eat!"
    ]
    random_event = random.choice(events)
    
    if "wild animal" in random_event:
        return dangerous_animal_event(player_id)
    
    return random_event


def dangerous_animal_event(player_id):
    choice = input("You encounter a dangerous animal! Do you want to (fight/flee)? ")
    
    if choice == "fight":
        # Placeholder for combat logic (can be expanded)
        if random.choice([True, False]):  # Random chance of winning
            return "You fought bravely and defeated the animal!"
        else:
            return "You were injured in the fight! Lose 10 health points."
    elif choice == "flee":
        return "You managed to escape safely!"
    else:
        return "Invalid choice. You hesitated and the animal attacked!"


def level_up(player_id):
    xp = get_xp(player_id)  # Function to retrieve XP
    if xp >= 100:  # Example threshold
        # Increase player level
        update_player_level(player_id)
        return "Congratulations! You've leveled up!"
    return "Keep gathering resources to level up!"





