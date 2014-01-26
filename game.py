from random import choice
from common import json_encode
from db import History
from geo import Geo
from dto import Spiel, Session
import random

class GameState(object):

    def __init__(self):
        self.players = {}
        self.history = History()
        self.geo = Geo()

    def add_player(self, session_id):
        r = lambda: random.randint(0,255)
        color = '#%02X%02X%02X' % (r(),r(),r())

        player_dto = Session(session_id, color)
        # self.players[session_id] = player_dto
        self.history.set_player(session_id, player_dto)
        return player_dto

    def remove_player(self, session_id):
        self.history.remove_player(session_id)
        del self.players[session_id]

    def get_player(self, session_id):
        return self.history.get_player(session_id)

    def get_block_id(self, latitude, longitude):
        return self.geo.get_block_id(latitude, longitude)

    def post_spiel(self, spiel):
        block_id = self.get_block_id(spiel._latitude, spiel._longitude)
        self.history.insert_spiel(block_id, spiel.json(), spiel.date)

    def post_spiel_to_block(self, block_id, spiel):
        self.history.insert_spiel(block_id, spiel.json(), spiel.date)

    def get_spiels_by_block_id(self, block_id, since=None, until=None):
        spiel_jsons = self.history.get_spiels(block_id, since, until)
        spiels = []
        for spiel_json in spiel_jsons:
            spiel = Spiel.from_json(spiel_json)
            spiels.append(spiel)

        return spiels

