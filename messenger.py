from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from game import GameState
from common import json_encode, json_decode, unix_now
from dto import DTO, Response, Spiel, Session, Block

class Connection(SockJSConnection):
    participants = set()
    game = GameState()

    def on_open(self, info):
        sessid = self.session.session_id
        self.session_id = sessid
        # Send that someone joined
        self.broadcast_text("{id} joined.".format(id=sessid))

        self.send_obj(Session(sessid))

        # Add client to the clients list
        self.participants.add(self)
        self.game.add_player(sessid)

        #periodic = ioloop.PeriodicCallback(self.send_state, 50)
        #periodic.start()

    def on_message(self, text):
        message = json_decode(text)
        session = message['session']
        if message['action'] == 'get_spiels':
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)
            spiels = self.get_spiels(latitude, longitude)

            for spiel in spiels:
                self.send_obj(spiel)

            block_id = self.game.get_block_id(latitude, longitude)
            self.send_obj(Block(block_id))
        if message['action'] == 'post_spiel':
            name = message['body']['name']
            spiel = message['body']['spiel']
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)

            if spiel and latitude and longitude:
                date = unix_now()
                spiel_dto = Spiel(name=name, spiel=spiel, latitude=latitude, longitude=longitude, date=date)
                self.notify_recipients(spiel_dto)
                self.game.post_spiel(spiel_dto)

    def on_close(self):
        sessid = self.session.session_id
        # Remove client from the clients list and broadcast leave message
        self.game.remove_player(sessid)
        self.participants.remove(self)
        self.broadcast_text("{id} left.".format(id=sessid))

    def debug(self, log):
        print log

    def response(self, dto):
        return Response(action=dto._action, body=dto).json()

    def send_obj(self, dto):
        self.send(self.response(dto))

    def notify_recipients(self, spiel):
        recipients = self.participants
        self.broadcast(recipients, self.response(spiel))

    def broadcast_text(self, text):
        json_message = json_encode({'action': 'log', 'body': {'message': text}})
        self.broadcast(self.participants, json_message)

    def get_spiels(self, latitude, longitude):
        spiels = self.game.get_spiels(latitude, longitude)
        return spiels

