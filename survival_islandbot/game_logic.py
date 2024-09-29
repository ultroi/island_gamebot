# game_bot.py

import random

class Game:
    def __init__(self):
        self.health = 5
        self.food = 3
        self.water = 3
        self.reputation = 0
        self.inventory = []
        self.scenes = {
            1: self.scene_1_storm,
            2: self.scene_2_waking_on_shore,
            3: self.scene_3_dense_jungle,
            4: self.scene_4_first_encounter,
            5: self.scene_5_village_welcome,
            6: self.scene_6_rival_tribes,
            7: self.scene_7_broken_shelter,
            8: self.scene_8_tribal_market,
            9: self.scene_9_hidden_ruins,
            10: self.scene_10_thieves_ambush,
        }
        self.current_scene = 1

    def start_game(self):
        while True:
            self.scenes[self.current_scene]()

    def update_resources(self):
        print(f"\nHealth: {self.health} | Food: {self.food} | Water: {self.water} | Reputation: {self.reputation} | Inventory: {self.inventory}")

    def explore(self):
        print("\n=== Exploration Phase ===")
        print("You venture into the surrounding area to gather resources.")
        encounter = random.choice(['nothing', 'wildlife', 'hidden_item', 'danger'])
        
        if encounter == 'wildlife':
            print("You encounter some wild animals!")
            action = input("\n[1] Observe them\n[2] Try to catch some food\nChoose an option: ")
            if action == '1':
                print("You observe the animals and learn about local wildlife.")
                self.reputation += 1
            else:
                print("You manage to catch a small animal for food!")
                self.food += 1
        
        elif encounter == 'hidden_item':
            print("You find a hidden stash of resources!")
            item = random.choice(['wood', 'water', 'artifact'])
            self.inventory.append(item)
            print(f"You found {item}!")
        
        elif encounter == 'danger':
            print("You step into a trap!")
            self.health -= 1
            print("You lost 1 health!")

    def scene_1_storm(self):
        print("\n=== Scene 1: The Storm ===")
        print("The sky darkens as Aria’s ship battles the raging sea...")
        self.explore()  # Exploration after the storm
        choice = input("\n[1] Fight the storm\n[2] Wait it out\nChoose an option: ")
        if choice == '1':
            self.current_scene = 2
        else:
            print("You waited too long and got thrown overboard!")
            self.current_scene = 2

    def scene_2_waking_on_shore(self):
        print("\n=== Scene 2: Waking on the Shore ===")
        print("Aria gasps for air as she washes ashore...")
        self.explore()  # Exploration after waking on shore
        choice = input("\n[1] Search for survivors\n[2] Gather supplies\nChoose an option: ")
        if choice == '1':
            print("You find Kimo, a villager!")
            self.reputation += 1
            self.current_scene = 3
        else:
            print("You gather some food and a makeshift weapon.")
            self.inventory.append("food")
            self.current_scene = 3

    def scene_3_dense_jungle(self):
        print("\n=== Scene 3: The Dense Jungle ===")
        print("With supplies in hand, Aria gazes at the dense jungle...")
        self.explore()  # Exploration in the dense jungle
        choice = input("\n[1] Enter the jungle\n[2] Stay at the beach\nChoose an option: ")
        if choice == '1':
            self.current_scene = 4
        else:
            print("You decide to signal for rescue but face hunger.")
            self.food -= 1
            self.current_scene = 4

    def scene_4_first_encounter(self):
        print("\n=== Scene 4: First Encounter with Kimo ===")
        print("After entering the jungle, Aria meets Kimo...")
        self.explore()  # Exploration before meeting Kimo
        choice = input("\n[1] Trust Kimo\n[2] Explore alone\nChoose an option: ")
        if choice == '1':
            print("Kimo teaches you about local plants and dangers.")
            self.current_scene = 5
        else:
            print("You miss valuable knowledge and face dangers alone.")
            self.current_scene = 5

    def scene_5_village_welcome(self):
        print("\n=== Scene 5: The Village Welcome ===")
        print("Kimo leads Aria to his coastal village...")
        self.explore()  # Exploration in the village
        choice = input("\n[1] Share your story\n[2] Keep it a secret\nChoose an option: ")
        if choice == '1':
            print("The villagers warm up to you.")
            self.reputation += 1
            self.current_scene = 6
        else:
            print("The villagers remain suspicious.")
            self.current_scene = 6

    def scene_6_rival_tribes(self):
        print("\n=== Scene 6: Rival Tribes ===")
        print("Rumors of rival tribes begin to surface...")
        self.explore()  # Exploration related to tribes
        choice = input("\n[1] Join the stronger tribe\n[2] Help the weaker tribe\nChoose an option: ")
        if choice == '1':
            print("You gain power but become a target.")
            self.reputation += 2
            self.current_scene = 7
        else:
            print("You earn their loyalty but resources are scarce.")
            self.reputation -= 1
            self.current_scene = 7

    def scene_7_broken_shelter(self):
        print("\n=== Scene 7: The Broken Shelter ===")
        print("You come across a broken shelter in the jungle...")
        self.explore()  # Exploration around the shelter
        choice = input("\n[1] Repair the shelter\n[2] Use it as is\nChoose an option: ")
        if choice == '1':
            print("You spend time fixing the shelter. It now offers better protection.")
            self.reputation += 1
            self.current_scene = 8
        else:
            print("You decide to stay in the broken shelter, risking exposure.")
            self.current_scene = 8

    def scene_8_tribal_market(self):
        print("\n=== Scene 8: The Tribal Market ===")
        print("You discover a bustling market with villagers trading goods...")
        self.explore()  # Exploration in the market
        choice = input("\n[1] Trade your food\n[2] Explore the market\nChoose an option: ")
        if choice == '1':
            print("You trade some food for fresh water and gain respect.")
            self.water += 1
            self.reputation += 1
            self.current_scene = 9
        else:
            print("You find a hidden gem but attract unwanted attention.")
            self.current_scene = 9

    def scene_9_hidden_ruins(self):
        print("\n=== Scene 9: Hidden Ruins ===")
        print("While exploring, you stumble upon ancient ruins...")
        self.explore()  # Exploration near the ruins
        choice = input("\n[1] Investigate further\n[2] Leave the ruins\nChoose an option: ")
        if choice == '1':
            print("You discover valuable artifacts that could help your journey.")
            self.inventory.append("artifact")
            self.current_scene = 10
        else:
            print("You leave the ruins, avoiding potential danger.")
            self.current_scene = 10

    def scene_10_thieves_ambush(self):
        print("\n=== Scene 10: Thieves' Ambush ===")
        print("As you leave the ruins, you are ambushed by thieves...")
        self.explore()  # Exploration before the ambush
        choice = input("\n[1] Fight back\n[2] Negotiate\nChoose an option: ")
        if choice == '1':
            print("You bravely fight off the thieves but sustain injuries.")
            self.health -= 1
            self.current_scene = 1  # Loop back or go to another scene
        else:
            print("You negotiate your way out, but lose some resources.")
            self.inventory.pop() if self.inventory else None  # Lose an item
            self.current_scene = 1  # Loop back or go to another scene

if __name__ == "__main__":
    game = Game()
    game.start_game()
