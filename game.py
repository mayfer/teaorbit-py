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

    def add_player(self, session_id):
        player = Player(color="#fff")
        self.players[session_id] = player
        return player

    def remove_player(self, session_id):
        del self.players[session_id]

    def get_block_id(self, latitude, longitude):
        return self.geo.get_block_id(latitude, longitude)

    def post_spiel(self, spiel):
        block_id = self.get_block_id(spiel._latitude, spiel._longitude)
        self.history.insert_spiel(block_id, spiel.json(), spiel.date)

    def post_spiel_to_block(self, block_id, spiel):
        self.history.insert_spiel(block_id, spiel.json(), spiel.date)

    def get_spiels_by_location(self, latitude, longitude):
        block_id = self.get_block_id(latitude, longitude)
        return self.get_spiels_by_block_id(block_id)

    def get_spiels_by_block_id(self, block_id):
        spiel_jsons = self.history.get_spiels(block_id)
        spiels = []
        for spiel_json in spiel_jsons:
            spiel = Spiel.from_json(spiel_json)
            spiels.append(spiel)

        return spiels

class Player(object):
    def __init__(self, color):
        self.color = color
