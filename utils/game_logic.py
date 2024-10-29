# utils/game_logic.py
import random
from models.event import Event

def generate_event():
    events = [
        Event("Find a berry bush", "You find a bush full of berries.", {"gain_health": 10}),
        Event("Encounter a wild animal", "A wild animal appears!", {"lose_health": 20}),
        Event("Discover a hidden cave", "You discover a hidden cave.", {"gain_item": "torch"})
    ]
    return random.choice(events)