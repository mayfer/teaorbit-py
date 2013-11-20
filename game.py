from random import choice
from common import json_encode
from db import History

class GameState(object):

    def __init__(self):
        self.players = {}
        self.history = History()
        print "Blank game initiated"

    def add_player(self, session_id):
        player = Player(session_id)
        self.players[session_id] = player
        return player

    def remove_player(self, session_id):
        if self.hat.owner == session_id:
            self.hat.owner = None
            self.hat.position.update(self.players[session_id].position.x, self.players[session_id].position.y)
        del self.players[session_id]

    def post_spiel(self, spiel):
        self.spiels.append(spiel)

    def dictify(self):
        players = {}
        hat = self.hat.dictify()
        for key, val in self.players.items():
            players[key] = val.dictify()
        return {'players': players, 'hat': hat}

class Player(object):
    # Guy types should be updated if new character models added
    guy_types = [1, 2, 3]

    def __init__(self, session_id):
        self.id = session_id
        # Player initial spawn position
        self.position = Position(0, 0)
        self.movement = Movement(0, 0)
        self.character = choice(self.guy_types)
        self.speech = None;

    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def dictify(self):
        return {'id': self.id, 'position': {'x': self.position.x, 'y': self.position.y}, 'character': self.character, 'movement': {'dx': self.movement.dx, 'dy': self.movement.dy}, 'speech': self.speech}

class Spiel(object):
    def __init__(self):
        # Initial starting position of hat defined here.
        self.position = Position(700, 700)
        self.owner = None

    def dictify(self):
        return { 'owner': self.owner, 'latitude': self.latitude, 'y': self.longitude }

    def json(self):
        return json_encode(self.dictify())

class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self, x, y):
        self.x = x
        self.y = y

class Movement(object):
    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def update(self, dx, dy):
        self.dx = dx
        self.dy = dy
