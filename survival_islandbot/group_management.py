from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_group, create_group, join_group, leave_group, get_group_members

def create_group_command(player_id, group_name):
    """
    Creates a new group with the given name.

    :param player_id: ID of the player creating the group
    :param group_name: Name of the group to create
    :return: Confirmation message
    """
    if create_group(player_id, group_name):
        return f"Group '{group_name}' has been created successfully!"
    return "Failed to create group. It may already exist."

def join_group_command(player_id, group_name):
    """
    Allows a player to join an existing group.

    :param player_id: ID of the player joining the group
    :param group_name: Name of the group to join
    :return: Confirmation message
    """
    if join_group(player_id, group_name):
        return f"You have joined the group '{group_name}'!"
    return "Failed to join group. Make sure the group name is correct."

def leave_group_command(player_id, group_name):
    """
    Allows a player to leave a group.

    :param player_id: ID of the player leaving the group
    :param group_name: Name of the group to leave
    :return: Confirmation message
    """
    if leave_group(player_id, group_name):
        return f"You have left the group '{group_name}'."
    return "Failed to leave group. You might not be a member."

def view_group_members_command(player_id, group_name):
    """
    Displays the members of a specific group.

    :param player_id: ID of the player requesting group members
    :param group_name: Name of the group to view members
    :return: List of group members
    """
    members = get_group_members(group_name)
    if members:
        member_list = "\n".join(members)
        return f"Members of '{group_name}':\n{member_list}"
    return "No members in this group or group does not exist."

def group_build_shelter_button(update, context):
    """
    Displays a button to initiate group shelter building.
    
    :param update: Update object from Telegram
    :param context: CallbackContext
    """
    keyboard = [
        [InlineKeyboardButton("Build Shelter", callback_data='build_group_shelter')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("What would you like to do?", reply_markup=reply_markup)

def handle_group_build_shelter(update, context):
    """
    Handles the action of building a shelter for the group.
    
    :param update: Update object from Telegram
    :param context: CallbackContext
    """
    query = update.callback_query
    query.answer()
    
    player_id = context.user_data['player_id']
    result = build_group_shelter(player_id)
    query.edit_message_text(text=result)

def build_group_shelter(player_id):
    """
    Logic for building a shelter collaboratively.
    
    :param player_id: ID of the player initiating the build
    :return: Message indicating success or failure
    """
    # Example placeholder logic for building a shelter
    if has_enough_resources(player_id):
        # Deduct resources and notify players
        return "You and your group successfully built a shelter!"
    return "You do not have enough resources to build a shelter."

def has_enough_resources(player_id):
    # Check resources logic
    return True  # Placeholder for actual resource check
