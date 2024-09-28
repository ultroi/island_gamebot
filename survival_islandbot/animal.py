class Animal:
    def __init__(self, name, damage, health_gain, resource_drop):
        self.name = name
        self.damage = damage
        self.health_gain = health_gain
        self.resource_drop = resource_drop

    def attack(self):
        # Return the damage dealt by the animal
        return self.damage

    def drop_resources(self):
        # Return the resources dropped by the animal
        return self.resource_drop

# Define animals as instances of the Animal class
ANIMALS = {
    "wolf": Animal(name="wolf", damage=10, health_gain=20, resource_drop={"meat": 2}),
    "bear": Animal(name="bear", damage=15, health_gain=30, resource_drop={"meat": 5}),
    "rabbit": Animal(name="rabbit", damage=5, health_gain=10, resource_drop={"meat": 1}),
}

def encounter_animal(player_id, animal_name):
    # Logic for encountering an animal
    animal = ANIMALS.get(animal_name)
    if animal:
        # Implement encounter logic (combat, fleeing, etc.)
        pass
