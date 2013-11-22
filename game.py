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
        del self.players[session_id]

    def post_spiel(self, spiel):
        self.history.append(spiel)


class Player(object):

    def __init__(self, session_id):
        self.id = session_id
        self.color = self.generate_color()

    def generate_color():
        return "#ffffff"

    def set_location(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def dictify(self):
        return {
            'id': self.id,
            'color': self.color,
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

class Spiel(object):
    def __init__(self):
        # Initial starting position of hat defined here.
        self.position = Position(700, 700)
        self.owner = None

    def dictify(self):
        return {
            'owner': self.owner,
            'latitude': self.latitude,
            'y': self.longitude
        }

    def json(self):
        return json_encode(self.dictify())

