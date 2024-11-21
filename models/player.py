from typing import List, Dict, Optional
import json
import os

class Player:
    _default_config = {
        "base_health": 100,
        "base_stamina": 50,
        "xp_multiplier": 1.5,
    }

    def __init__(
        self,
        user_id: str,
        name: str,
        level: int = 1,
        experience: int = 0,
        stats: Optional[Dict[str, int]] = None,
        inventory: Optional[List[Dict]] = None,
        location: str = "Starting Point",
        exploration_progress: int = 0,
        started_adventure: bool = False,
        arc_type: Optional[str] = None,
        config_path: str = '/workspaces/island_gamebot/data/config.json'
    ):
        # Basic Attributes
        self.user_id = user_id
        self.name = name
        self.level = level
        self.experience = experience
        self.location = location
        self.exploration_progress = exploration_progress
        self.started_adventure = started_adventure
        self.arc_type = arc_type

        # Inventory
        self.inventory = inventory if inventory is not None else []

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize stats
        self.stats = stats if stats else self._initialize_stats()

    def _load_config(self, config_path: str) -> dict:
        """Load the configuration from a JSON file or use a default config."""
        if not os.path.exists(config_path):
            print(f"Warning: Config file not found: {config_path}. Using default configuration.")
            return self._default_config
        try:
            with open(config_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}. Using default configuration.")
            return self._default_config

    def _initialize_stats(self) -> Dict[str, int]:
        """Initialize player stats dynamically based on level and configuration."""
        base_health = self.config.get("base_health", 100)
        base_stamina = self.config.get("base_stamina", 50)
        return {
            "health": base_health + (self.level * 10),
            "max_health": base_health + (self.level * 10),
            "stamina": base_stamina + (self.level * 5),
            "max_stamina": base_stamina + (self.level * 5),
        }

    def update_stat(self, stat_name: str, value: int):
        """Update or add a player stat dynamically."""
        self.stats[stat_name] = value

    def gain_experience(self, amount: int):
        """Add experience to the player and handle leveling up."""
        self.experience += amount
        max_xp = self.get_max_experience()
        while self.experience >= max_xp:
            self.experience -= max_xp
            self.level_up()

    def get_max_experience(self) -> int:
        """Calculate the maximum experience for the current level."""
        multiplier = self.config.get("xp_multiplier", 1.5)
        return int(100 * (self.level ** multiplier))

    def level_up(self):
        """Increase the player's level and update stats."""
        self.level += 1
        self.stats["max_health"] += 10
        self.stats["max_stamina"] += 5
        self.stats["health"] = self.stats["max_health"]
        self.stats["stamina"] = self.stats["max_stamina"]
        print(f"{self.name} leveled up to level {self.level}!")

    def take_damage(self, amount: int):
        """Reduce health by the damage amount."""
        self.stats["health"] -= amount
        if self.stats["health"] <= 0:
            self.stats["health"] = 0
            print(f"{self.name} has been defeated!")

    def heal(self, amount: int):
        """Heal the player by a specific amount."""
        self.stats["health"] += amount
        if self.stats["health"] > self.stats["max_health"]:
            self.stats["health"] = self.stats["max_health"]

    def to_dict(self) -> Dict:
        """Convert the Player object to a dictionary."""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "level": self.level,
            "experience": self.experience,
            "stats": self.stats,
            "inventory": self.inventory,
            "location": self.location,
            "exploration_progress": self.exploration_progress,
            "started_adventure": self.started_adventure,
            "arc_type": self.arc_type,
        }

    def save_to_json(self, file_path: str):
        """Save the player object to a JSON file."""
        try:
            with open(file_path, 'w') as file:
                json.dump(self.to_dict(), file, indent=4)
        except IOError as e:
            print(f"Error saving player data: {e}")

    @classmethod
    def from_dict(cls, data: Dict, config_path: str = '/workspaces/island_gamebot/data/config.json') -> "Player":
        """Create a Player object from a dictionary."""
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            stats=data.get("stats", {}),
            inventory=data.get("inventory", []),
            location=data.get("location", "Starting Point"),
            exploration_progress=data.get("exploration_progress", 0),
            started_adventure=data.get("started_adventure", False),
            arc_type=data.get("arc_type"),
            config_path=config_path
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
