from typing import List, Dict, Optional
from utils.shared_utils import calculate_max_xp

class Player:
    def __init__(self, 
                 user_id: int, 
                 name: str, 
                 health: int = 100, 
                 max_health: int = 100, 
                 inventory: Optional[List[str]] = None, 
                 location: str = 'beach', 
                 explorations: int = 0, 
                 experience: int = 0, 
                 stamina: int = 50,
                 max_stamina: int = 50,
                 started_adventure: bool = False,
                 level: int = 1,
                 arc_type: str = 'survival'):
        self.user_id = user_id
        self.name = name
        self.level = level
        self.arc_type = arc_type

        # Max Health and Max Stamina increase as level increases
        self.max_health = max_health
        self.max_stamina = max_stamina

        # Current Health and Stamina are set to max initially, but can change
        self.health = health if health <= self.max_health else self.max_health
        self.stamina = stamina if stamina <= self.max_stamina else self.max_stamina

        # Experience and Level system
        self.experience = experience
        self.max_experience = calculate_max_xp(self.level)  # Calculate the max XP required for next level
        self.location = location
        self.explorations = explorations
        self.started_adventure = started_adventure

        # Initialize inventory
        self.inventory = inventory if inventory is not None else []

    def to_dict(self) -> Dict:
        """Convert Player instance to a dictionary for easy storage."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'health': self.health,
            'max_health': self.max_health,
            'inventory': self.inventory,
            'location': self.location,
            'explorations': self.explorations,
            'experience': self.experience,
            'stamina': self.stamina,
            'max_stamina': self.max_stamina,
            'started_adventure': self.started_adventure,
            'level': self.level,
            'arc_type': self.arc_type
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        """Create a Player instance from a dictionary."""
        return cls(
            user_id=data['user_id'],
            name=data['name'],
            health=data.get('health', 100),
            max_health=data.get('max_health', 100),
            stamina=data.get('stamina', 50),
            max_stamina=data.get('max_stamina', 50),
            inventory=data.get('inventory', []),
            location=data.get('location', 'beach'),
            explorations=data.get('explorations', 0),
            experience=data.get('experience', 0),
            started_adventure=data.get('started_adventure', False),
            level=data.get('level', 1),
            arc_type=data.get('arc_type', 'survival')
        )
