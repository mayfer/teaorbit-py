from random import choice
from common import json_encode
from db import History
from messages import SpielView, SessionView
import random

class GameState(object):

    def __init__(self):
        self.players = {}
        self.history = History()

    def add_player(self, session_id):
        r = lambda: random.randint(0,255)
        color = '#%02X%02X%02X' % (r(),r(),r())

        player_dto = SessionView(session_id, color)
        # self.players[session_id] = player_dto
        self.history.set_player(session_id, player_dto)
        return player_dto

    def get_player(self, session_id):
        return self.history.get_player(session_id)

    def post_spiel(self, spiel):
        room_id = self.get_room_id(spiel._latitude, spiel._longitude)
        self.history.insert_spiel(room_id, spiel.json(), spiel.date)

    def post_private_spiel(self, to_id, pv_spiel):
        self.history.insert_private_spiel(to_id, spiel.json(), spiel.date)

    def post_spiel_to_room(self, room_id, spiel):
        self.history.insert_spiel(room_id, spiel.json(), spiel.date)

    def get_spiels_by_room_id(self, room_id, since=None, until=None):
        spiel_jsons = self.history.get_spiels(room_id, since, until)
        spiels = []
        for spiel_json in spiel_jsons:
            spiel = SpielView.from_json(spiel_json)
            spiels.append(spiel)

        return spiels

