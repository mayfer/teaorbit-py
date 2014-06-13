from common import generate_unique_id
from messages import DTO
import random

class Model(DTO):
    pass

class Room(Model):
    def __init__(self, name):
        self.name = name
        self.subscribers = []

class Session(Model):
    def __init__(self, session_id, color=None, public_id=None):
        self.session_id = session_id

        if public_id is None:
            public_id = generate_unique_id()[:10]

        self.public_id = public_id

        if color is None:
            r = lambda: random.randint(0,255)
            color = '#%02X%02X%02X' % (r(),r(),r())

        self.color = color

class SubscriptionManager(Model):
    def __init__(self):
        self.subscriptions = {}

class Spiel(DTO):
    def __init__(self, name='', spiel='', date=None, color=None):
        self.name = name
        self.spiel = spiel
        self.date = date
        self.color = color

    @classmethod
    def from_model(self, spiel_model):
        sm = spiel_model
        return SpielView(
            name = sm.name,
            spiel = sm.spiel,
            date = sm.date,
            color = sm.color,
        )
