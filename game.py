from random import choice
from common import json_encode
from db import History
from geo import Geo

class GameState(object):

    def __init__(self):
        self.players = {}
        self.history = History()
        self.geo = Geo()
        print "Blank world initiated"

    def add_player(self, session_id):
        self.players[session_id] = True

    def remove_player(self, session_id):
        del self.players[session_id]

    def post_spiel(self, spiel):
        block_id = self.geo.get_block_id(spiel.latitude, spiel.longitude)
        self.history.insert_spiel(block_id, spiel)

    def get_spiels(self, since_timestamp, latitude, longitude):
        block_id = self.geo.get_block_id(latitude, longitude)
        self.history.get_spiels(block_id, since_timestamp)


