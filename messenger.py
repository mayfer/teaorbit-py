from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from game import GameState, Player
from common import json_encode, json_decode

class Connection(SockJSConnection):
    participants = set()
    game_state = GameState()

    def on_open(self, info):
        sessid = self.session.session_id
        # Send that someone joined
        self.broadcast_text("{id} joined.".format(id=sessid))

        self.send_obj('session', {'session_id': sessid})

        # Add client to the clients list
        self.participants.add(self)
        self.game_state.add_player(sessid)

        self.debug()
        #periodic = ioloop.PeriodicCallback(self.send_state, 50)
        #periodic.start()

    def on_message(self, text):
        message = json_decode(text)
        if message['action'] == 'get_spiels':
            session = message['body']['session']
            latitude = message['body']['latitude']
            longitude = message['body']['longitude']
            spiels = self.get_state_since(message['body']['since'], latitude, longitude)
            self.send_obj('spiels', spiels)
        if message['action'] == 'post_spiel':
            session = message['body']['session']
            name = message['body']['name']
            spiel = message['body']['spiel']
            latitude = message['body']['latitude']
            longitude = message['body']['longitude']
            self.send_obj('ack', {'something': 'worked'})
            self.notify_recipients(name, spiel, latitude, longitude)

    def on_close(self):
        sessid = self.session.session_id
        # Remove client from the clients list and broadcast leave message
        self.game_state.remove_player(sessid)
        self.participants.remove(self)
        self.broadcast_text("{id} left.".format(id=sessid))
        self.debug()

    def debug(self):
        print self.game_state.__dict__

    def send_obj(self, action, obj):
        self.send(json_encode({'action': action, 'body': obj}))

    def notify_recipients(self, name, spiel, latitude, longitude):
        recipients = self.participants
        json_message = json_encode({
            'action': 'new_post',
            'body': {
                'name': name,
                'spiel': spiel,
            }
        })
        self.broadcast(recipients, json_message)

    def broadcast_text(self, text):
        json_message = json_encode({'action': 'log', 'body': {'message': text}})
        self.broadcast(self.participants, json_message)

    def send_state(self):
        self.send_obj('state', self.game_state.dictify())

    def get_state_since(self, since_id, latitude, longitude):
        spiels = [
            {'name': 'Muratti', 'spiel': 'Ratatat'},
            {'name': 'sup', 'spiel': 'Hllo Wrld'},
        ]
        return spiels

