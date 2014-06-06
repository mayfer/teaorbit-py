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
    def __init__(self, session_id):
        self.session_id = session_id
        self.public_id = generate_unique_id()[:10]

        r = lambda: random.randint(0,255)
        self.color = '#%02X%02X%02X' % (r(),r(),r())

class SubscriptionManager(Model):
    def __init__(self):
        self.subscriptions = {}

