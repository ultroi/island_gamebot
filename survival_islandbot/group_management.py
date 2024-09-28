from database import get_player_group, add_player_to_group, remove_player_from_group, notify_player
from utils import get_player_id

MIN_GROUP_SIZE = 2  # Minimum number of members required to explore
MAX_GROUP_SIZE = 5  # Maximum number of members allowed in a group

class GroupManager:
    def __init__(self):
        self.groups = {}  # To hold groups in memory (for quick access)

    def create_group(self, player_id, group_name):
        """
        Create a new group if it doesn't exist.
        
        :param player_id: ID of the player creating the group
        :param group_name: Name of the group to create
        :return: Message indicating success or failure
        """
        if group_name in self.groups:
            return "Group already exists."
        
        self.groups[group_name] = {
            'members': [player_id]
        }
        notify_player(player_id, f"You have created the group '{group_name}'!")
        return f"Group '{group_name}' created successfully."

    def join_group(self, player_id, group_name):
        """
        Allow a player to join an existing group.
        
        :param player_id: ID of the player joining the group
        :param group_name: Name of the group to join
        :return: Message indicating success or failure
        """
        if group_name not in self.groups:
            return "Group does not exist."
        
        if len(self.groups[group_name]['members']) >= MAX_GROUP_SIZE:
            return "Group is full. You cannot join."

        self.groups[group_name]['members'].append(player_id)
        notify_player(player_id, f"You have joined the group '{group_name}'!")
        return f"You joined the group '{group_name}' successfully."

    def leave_group(self, player_id, group_name):
        """
        Allow a player to leave a group.
        
        :param player_id: ID of the player leaving the group
        :param group_name: Name of the group to leave
        :return: Message indicating success or failure
        """
        if group_name not in self.groups or player_id not in self.groups[group_name]['members']:
            return "You are not a member of this group."

        self.groups[group_name]['members'].remove(player_id)
        notify_player(player_id, f"You have left the group '{group_name}'.")
        
        if len(self.groups[group_name]['members']) == 0:
            del self.groups[group_name]  # Delete the group if empty

        return f"You left the group '{group_name}' successfully."

    def invite_player(self, player_id, target_player_id, group_name):
        """
        Invite another player to the group.
        
        :param player_id: ID of the player sending the invite
        :param target_player_id: ID of the player to invite
        :param group_name: Name of the group to invite to
        :return: Message indicating success or failure
        """
        if group_name not in self.groups:
            return "Group does not exist."
        
        if target_player_id in self.groups[group_name]['members']:
            return f"{target_player_id} is already in the group."

        # Notify the invited player (you may implement a method to send an invitation)
        notify_player(target_player_id, f"You have been invited to join the group '{group_name}' by {player_id}.")
        return f"Invitation sent to {target_player_id}."

    def kick_player(self, player_id, target_player_id, group_name):
        """
        Kick a player from the group.
        
        :param player_id: ID of the player kicking someone
        :param target_player_id: ID of the player to kick
        :param group_name: Name of the group to kick from
        :return: Message indicating success or failure
        """
        if group_name not in self.groups or player_id not in self.groups[group_name]['members']:
            return "You are not in this group."

        if target_player_id not in self.groups[group_name]['members']:
            return f"{target_player_id} is not in this group."

        self.groups[group_name]['members'].remove(target_player_id)
        notify_player(target_player_id, f"You have been kicked from the group '{group_name}'.")
        return f"{target_player_id} has been kicked from the group '{group_name}'."

    def can_explore(self, group_name):
        """
        Check if the group can start exploring based on its size.
        
        :param group_name: The name of the group to check
        :return: Boolean indicating whether the group can explore
        """
        if group_name not in self.groups:
            return False  # Group does not exist
        member_count = len(self.groups[group_name]['members'])
        return MIN_GROUP_SIZE <= member_count <= MAX_GROUP_SIZE

    def start_exploration(self, player_id):
        """
        Start exploration if the group meets the size requirements.
        
        :param player_id: ID of the player initiating exploration
        :return: Message indicating whether exploration can start
        """
        group_name = get_player_group(player_id)
        if not group_name:
            return "You are not in any group."
        
        if not self.can_explore(group_name):
            return f"Your group must have between {MIN_GROUP_SIZE} and {MAX_GROUP_SIZE} members to start exploring."

        # Proceed with exploration logic
        return self.explore_group(group_name)

    def explore_group(self, group_name):
        """
        Placeholder for actual exploration logic.
        
        :param group_name: The name of the group exploring
        :return: Exploration result message
        """
        return f"The group '{group_name}' starts exploring the island!"

# Example command integration for bot
def create_group_command(player_id, group_name):
    manager = GroupManager()
    result = manager.create_group(player_id, group_name)
    notify_player(player_id, result)

def join_group_command(player_id, group_name):
    manager = GroupManager()
    result = manager.join_group(player_id, group_name)
    notify_player(player_id, result)

def leave_group_command(player_id, group_name):
    manager = GroupManager()
    result = manager.leave_group(player_id, group_name)
    notify_player(player_id, result)

def invite_player_command(player_id, target_player_id, group_name):
    manager = GroupManager()
    result = manager.invite_player(player_id, target_player_id, group_name)
    notify_player(player_id, result)

def kick_player_command(player_id, target_player_id, group_name):
    manager = GroupManager()
    result = manager.kick_player(player_id, target_player_id, group_name)
    notify_player(player_id, result)

def start_exploration_command(player_id):
    manager = GroupManager()
    result = manager.start_exploration(player_id)
    notify_player(player_id, result)
