from common import generate_unique_id
from messages import DTO
import random

class Model(DTO):
    pass

class Room(Model):
    def __init__(self, name):
        self.name = name
        self.subscribers = []

class RoomSession(Model):
    def __init__(self, name, session):
        self.name = name
        self.session = session

class Session(Model):
    def __init__(self, session_id, color=None, public_id=None, last_active=0):
        self.session_id = session_id
        self.last_active = last_active

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
    def __init__(self, id='', name='', spiel='', date=None, color=None):
        self.id = id
        self.name = name
        self.spiel = spiel
        self.date = date
        self.color = color

