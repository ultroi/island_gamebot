# models/event.py
class Event:
    def __init__(self, name, description, outcomes):
        self.name = name
        self.description = description
        self.outcomes = outcomes