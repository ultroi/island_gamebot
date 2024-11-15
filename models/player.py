from typing import List, Dict, Optional

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
                 stamina: int = 50):  # Add stamina with default value 50
        self.user_id = user_id
        self.name = name
        self.health = health
        self.max_health = max_health
        self.inventory = inventory if inventory is not None else []
        self.location = location
        self.explorations = explorations
        self.experience = experience
        self.stamina = stamina  # Initialize stamina

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
            'stamina': self.stamina  # Include stamina in the dictionary
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        """Create a Player instance from a dictionary."""
        return cls(
            user_id=data.get('user_id'),
            name=data.get('name'),
            health=data.get('health', 100),
            max_health=data.get('max_health', 100),
            inventory=data.get('inventory', []),
            location=data.get('location', 'beach'),
            explorations=data.get('explorations', 0),
            experience=data.get('experience', 0),
            stamina=data.get('stamina', 50)  # Get stamina from dictionary, default to 50 if not found
        )

    def add_to_inventory(self, item: str) -> None:
        """Add an item to the player's inventory."""
        self.inventory.append(item)

    def remove_from_inventory(self, item: str) -> bool:
        """Remove an item from the player's inventory if it exists."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def adjust_health(self, amount: int) -> None:
        """Adjust the player's health, ensuring it doesn't exceed max or go below zero."""
        self.health = max(0, min(self.health + amount, self.max_health))

    def change_location(self, new_location: str) -> None:
        """Change the player's location."""
        self.location = new_location

    def increment_exploration(self) -> None:
        """Increment the number of explorations the player has undertaken."""
        self.explorations += 1

    def add_experience(self, points: int) -> None:
        """Increase the player's experience by a given number of points."""
        self.experience += points

    def adjust_stamina(self, amount: int) -> None:
        """Adjust the player's stamina, ensuring it doesn't exceed max or go below zero."""
        self.stamina = max(0, min(self.stamina + amount, 100))  # Max stamina is 100

