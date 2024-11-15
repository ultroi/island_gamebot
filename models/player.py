import random
import time

class Player:
    def __init__(self, name, level=1, health=100, stamina=100):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = 100 + (level * 10)  # Health scales with level
        self.stamina = stamina
        self.max_stamina = 100 + (level * 5)  # Stamina scales with level
        self.location = "Beach"  # Starting location
        self.inventory = []
        self.current_xp = 0
        self.total_xp = 1000 * level  # Example XP formula

    def explore(self):
        if self.stamina >= 20:
            self.stamina -= 20  # Decrease stamina by 20 per exploration
            print(f"Exploring... Stamina left: {self.stamina}")
            return True
        else:
            print("Not enough stamina to explore!")
            return False

    def rest(self):
        if self.stamina < self.max_stamina:
            self.stamina += 10  # Regenerate 10 stamina every rest cycle
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina
            print(f"Resting... Stamina now: {self.stamina}")
        else:
            print("Stamina is already full!")

    def consume_food(self, food_type):
        if food_type == "apple":
            self.stamina += 15  # Apple gives a stamina boost
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina
            print(f"Eating apple... Stamina now: {self.stamina}")
        elif food_type == "meat":
            self.health += 20  # Meat restores health
            if self.health > self.max_health:
                self.health = self.max_health
            print(f"Eating meat... Health now: {self.health}")
