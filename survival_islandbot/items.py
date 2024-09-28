class Item:
    def __init__(self, name, value, description, effects=None):
        self.name = name
        self.value = value
        self.description = description
        self.effects = effects or {}

# Food items with effects
FOOD_TYPES = {
    "berries": Item(name="berries", value=5, description="A handful of fresh berries.", effects={"health": 10}),
    "meat": Item(name="meat", value=10, description="Cooked meat from a wild animal.", effects={"health": 20}),
    "fish": Item(name="fish", value=7, description="A fish caught from the river.", effects={"health": 15}),
}

# Weapon items with effects
WEAPON_STATS = {
    "spear": Item(name="spear", value=10, description="A long-range spear for hunting.", effects={"damage": 10}),
    "axe": Item(name="axe", value=15, description="A sturdy axe for chopping wood and fighting.", effects={"damage": 15}),
    "bow": Item(name="bow", value=12, description="A bow for long-distance attacks.", effects={"damage": 12}),
}

# Armor items with effects
ARMOR_STATS = {
    "leather armor": Item(name="leather armor", value=20, description="Light armor made of leather.", effects={"protection": 5}),
    "chainmail armor": Item(name="chainmail armor", value=35, description="Heavy armor made of chainmail.", effects={"protection": 10}),
}
