from resources.items import get_item_recipe, get_all_recipes
from database import get_resources, update_resources
from utils import notify_player, send_message_with_buttons

def craft_item(player_id, item_name):
    """
    Allows the player to craft an item if they have the required resources.
    
    :param player_id: ID of the player crafting the item
    :param item_name: Name of the item to craft
    :return: Message indicating success or failure
    """
    # Fetch the item's recipe
    recipe = get_item_recipe(item_name)
    if not recipe:
        return "Unknown item. Please check the item name."

    # Get player resources
    player_resources = get_resources(player_id)
    
    # Check if the player has enough resources
    if all(player_resources.get(res_type, 0) >= amount for res_type, amount in recipe.items()):
        # Deduct resources required for crafting
        for res_type, amount in recipe.items():
            update_resources(player_id, {res_type: -amount})
        
        # Notify player and return success message
        notify_player(player_id, f"Successfully crafted {item_name}!")
        return f"You crafted a {item_name}."
    
    return "You don't have enough resources to craft this item."


def list_craftable_items(player_id):
    """
    Lists items that the player can craft based on their current resources and shows buttons for crafting.
    
    :param player_id: ID of the player checking craftable items
    :return: List of items that can be crafted with buttons
    """
    craftable_items = []
    player_resources = get_resources(player_id)
    
    # Check each recipe and see if the player has enough resources to craft the item
    for item_name in get_all_recipes():
        recipe = get_item_recipe(item_name)
        
        if all(player_resources.get(res_type, 0) >= amount for res_type, amount in recipe.items()):
            craftable_items.append(item_name)

    if craftable_items:
        # Send a message with inline buttons for each craftable item
        send_message_with_buttons(player_id, "You can craft the following items:", craftable_items)
        return
    else:
        notify_player(player_id, "You don't have enough resources to craft any items.")


def show_player_resources(player_id):
    """
    Displays the current status of the player's resources.
    
    :param player_id: ID of the player whose resources to display
    :return: String with the player's current resources
    """
    player_resources = get_resources(player_id)
    
    # Format resource status
    resource_status = "\n".join([f"{res_type.capitalize()}: {amount}" for res_type, amount in player_resources.items()])
    
    notify_player(player_id, f"Your current resources are:\n{resource_status}")
