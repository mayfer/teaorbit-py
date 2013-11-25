from random import choice
from common import json_encode
from db import History
from geo import Geo
from dto import Spiel

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
        self.history.insert_spiel(block_id, spiel.json(), spiel.date)

    def get_spiels(self, latitude, longitude):
        block_id = self.geo.get_block_id(latitude, longitude)
        spiel_jsons = self.history.get_spiels(block_id)
        spiels = []
        for spiel_json in spiel_jsons:
            spiel = Spiel.from_json(spiel_json)
            spiels.append(spiel)

        return spiels
