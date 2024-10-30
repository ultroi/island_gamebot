# models/player.py
class Player:
    def __init__(self, user_id, name, health=100, max_health=100, inventory=None, location='beach', explorations=0):
        self.user_id = user_id
        self.name = name
        self.health = health
        self.max_health = max_health
        self.inventory = inventory if inventory else []
        self.location = location
        self.explorations = explorations

    def to_dict(self):
        return {
            'name': self.name,
            'user_id': self.user_id,
            'health': self.health,
            'max_health': self.max_health,
            'inventory': self.inventory,  # Keep as list
            'location': self.location,
            'explorations': self.explorations
        }