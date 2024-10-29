# models/player.py
class Player:
    def __init__(self, user_id, health=100, inventory=None, location='beach'):
        self.user_id = user_id
        self.health = health
        self.inventory = inventory if inventory else []
        self.location = location

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'health': self.health,
            'inventory': ','.join(self.inventory),
            'location': self.location
        }