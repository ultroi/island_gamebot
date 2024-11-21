from typing import List, Dict, Optional
from utils.shared_utils import get_max_health, get_max_stamina, get_level_xp
import json
import os


class Player:
    def __init__(
        self, 
        user_id: str, 
        name: str, 
        level: int = 1, 
        experience: int = 0, 
        health: Optional[int] = None,
        max_health: Optional[int] = None, 
        stamina: Optional[int] = None,
        max_stamina: Optional[int] = None,
        inventory: Optional[List[Dict]] = None,  
        location: str = "Starting Point",  # Default location
        exploration_progress: int = 0,
        started_adventure: bool = False,  # Add started_adventure attribute
        arc_type: Optional[str] = None,  # Add arc_type attribute
        config_path: str = '/workspaces/island_gamebot/data/config.json'  # Default path to config file

    ):
        self.user_id = user_id
        self.name = name
        self.level = level
        self.experience = experience
        self.inventory = inventory if inventory is not None else []  # Initialize inventory
        self.location = location  # Set the player's location
        self.exploration_progress = exploration_progress
        self.started_adventure = started_adventure  # Initialize started_adventure
        self.arc_type = arc_type  # Initialize arc_type

        # Load the configuration
        self.config = self._load_config(config_path)

        # Initialize health and stamina based on the level and config
        self.max_health = max_health if max_health is not None else get_max_health(level, self.config)
        self.health = max_health if max_health is not None else self.max_health
        self.max_stamina = max_stamina if max_stamina is not None else get_max_stamina(level, self.config)
        self.stamina = max_stamina if max_stamina is not None else self.max_stamina
        self.max_experience = get_level_xp(level)  # Calculate max_experience based on the level
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from the provided file path."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse config file: {e}")

    def update_stat(self, stat_name: str, value: int):
        """Update a specific player stat."""
        if hasattr(self, stat_name):
            setattr(self, stat_name, value)
        else:
            raise AttributeError(f"Player has no attribute '{stat_name}'")

    def to_dict(self) -> Dict:
        """Convert the Player object to a dictionary for serialization."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "health": self.health,
            "max_health": self.max_health,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "max_experience": self.max_experience,
            "inventory": self.inventory,
            "location": self.location,  # Include location in dict
            "started_adventure": self.started_adventure,  # Include started_adventure in dict
            "arc_type": self.arc_type  # Include arc_type in dict
        }

    def save_to_json(self, file_path: str):
        """Save the player object to a JSON file."""
        try:
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)
        except IOError as e:
            raise IOError(f"Failed to save player data: {e}")

    @classmethod
    def from_dict(cls, data: Dict, config_path: str = '/workspaces/island_gamebot/data/config.json') -> "Player":
        """Create a Player object from a dictionary."""
        
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            health=data.get("health"),
            max_health=data.get("max_health"),
            stamina=data.get("stamina"),
            max_stamina=data.get("max_stamina"),
            inventory=data.get("inventory", []),
            location=data.get("location", "Starting Point"),  # Default to 'Starting Point' if not in data
            exploration_progress=data.get("exploration_progress", 0),
            config_path=config_path,
            started_adventure=data.get("started_adventure", False),  # Default to False if not in data
            arc_type=data.get("arc_type")  # Get arc_type from data
        )

    @classmethod
    def load_from_json(cls, file_path: str, config_path: str = '/workspaces/island_gamebot/data/config.json') -> "Player":
        """Load a Player object from a JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Player file not found: {file_path}")
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return cls.from_dict(data, config_path)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse player file: {e}")

 

