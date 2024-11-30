from typing import List, Dict, Optional
import json
import os

class Player:
    _default_config = {
        "base_health": 60,
        "base_stamina": 50,
        "health_per_level": 10,
        "stamina_per_level": 3,
        "xp_multiplier": 1.5,
        "xp_per_item": 2,
        "xp_per_encounter": 5,
        "level_cap": 10,
        "biome_effects": {
            "beach": 0,
            "mountain": 5,
            "caves": -5,
            "desert": -10,
        },
        "endurance_effects": {
            "low_stamina_penalty": {
                "movement_speed": -20,
                "action_delay": 2,
            },
            "low_health_penalty": {
                "vision_blur": True,
                "recovery_rate": -50,
            }
        },
        "space_per_item": {
            "common": 5,
            "rare": 8
        }
    }

    def __init__(
        self,
        user_id: str,
        name: str,
        level: int = 1,
        experience: int = 0,
        location: str = "Beach",
        stats: Optional[Dict[str, int]] = None,
        inventory: Optional[List[Dict]] = None,
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
        base_health = self.config.get("base_health", 60)
        base_stamina = self.config.get("base_stamina", 50)
        health_per_level = self.config.get("health_per_level", 10)
        stamina_per_level = self.config.get("stamina_per_level", 3)

        return {
            "health": base_health + (self.level * health_per_level),
            "max_health": base_health + (self.level * health_per_level),
            "stamina": base_stamina + (self.level * stamina_per_level),
            "max_stamina": base_stamina + (self.level * stamina_per_level),
        }

    @property
    def health(self):
        return self.stats["health"]

    @health.setter
    def health(self, value: int):
        self.stats["health"] = self._clamp(value, 0, self.stats["max_health"])

    @property
    def stamina(self):
        return self.stats["stamina"]

    @stamina.setter
    def stamina(self, value: int):
        self.stats["stamina"] = self._clamp(value, 0, self.stats["max_stamina"])

    def _clamp(self, value: int, min_value: int, max_value: int) -> int:
        """Clamp a value between a minimum and maximum."""
        return max(min_value, min(value, max_value))
    
    def change_location(self, new_location: str):
        """Change the player's location and apply the new biome effects."""
        if new_location != self.location:
            print(f"{self.name} is moving to {new_location}.")
            self.location = new_location
            self.apply_biome_effect()

    def gain_experience(self, amount: int):
        """Add experience to the player and handle leveling up."""
        self.experience += amount
        max_xp = self.get_max_experience()
        while self.experience >= max_xp:
            self.experience -= max_xp
            self.level_up()
            max_xp = self.get_max_experience()  # Recalculate max XP for the new level

    def get_max_experience(self) -> int:
        """Calculate the maximum experience for the current level."""
        # Increase XP requirement per level more steeply to make leveling harder
        multiplier = self.config.get("xp_multiplier", 2.0)  # Hardcore survival: steeper multiplier
        base_xp = 100  # Base XP for level 1
        return int(base_xp * (self.level ** multiplier))  # Exponentially increasing XP requirement

    def level_up(self):
        """Increase the player's level and update stats."""
        if self.level >= self.config.get("level_cap", 20):  # Increased level cap for hardcore survival
            print(f"{self.name} has reached the level cap!")
            return

        self.level += 1
        # Increase stats more aggressively per level
        self.stats["max_health"] += self.config.get("health_per_level")  # More health per level
        self.stats["max_stamina"] += self.config.get("stamina_per_level")  # More stamina per level
        self.health = self.stats["max_health"]
        self.stamina = self.stats["max_stamina"]
        print(f"{self.name} leveled up to level {self.level}!")


    def take_damage(self, amount: int):
        """Reduce health by the damage amount."""
        self.health -= amount
        if self.health <= 0:
            print(f"{self.name} has been defeated!")

    def restore_stamina(self, amount: int):
        """Restore stamina up to the maximum limit."""
        self.stamina += amount

    def reduce_stamina(self, amount: int):
        """Reduce stamina and handle exhaustion."""
        self.stamina -= amount
        if self.stamina == 0:
            print(f"{self.name} is exhausted!")

    def heal(self, amount: int):
        """Heal the player by a specific amount."""
        self.health += amount

    def apply_biome_effect(self):
        """Apply biome effects to the player based on their location."""
        biome = self.location.lower()
        biome_effect = self.config["biome_effects"].get(biome, 0)
        self.stats["max_stamina"] += biome_effect
        self.stamina = self.stats["max_stamina"]
        print(f"Biome effect applied: {biome}.")

    def apply_endurance_penalties(self):
        """Apply penalties based on stamina and health levels."""
        if self.stamina < self.stats["max_stamina"] * 0.2:
            penalty = self.config["endurance_effects"]["low_stamina_penalty"]
            print(f"Stamina low! Movement speed reduced by {penalty['movement_speed']}% and action delay increased by {penalty['action_delay']}s.")
        
        if self.health < self.stats["max_health"] * 0.2:
            penalty = self.config["endurance_effects"]["low_health_penalty"]
            if penalty["vision_blur"]:
                print("Health low! Vision is blurred.")
            self.stats["recovery_rate"] = penalty["recovery_rate"]
    
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
            location=data.get("location"),
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
