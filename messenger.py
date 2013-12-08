from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from game import GameState
from common import json_encode, json_decode, unix_now, unix_now_ms
from dto import DTO, Response, Spiel, Session, Block, OnlineUsers

class Connection(SockJSConnection):
    participants = set()
    rooms = {}
    sessions = {}
    game = GameState()

    def on_open(self, info):
        if 'session' in info.cookies:
            session_id = info.cookies['session'].value
        else:
            session_id = self.session.session_id

        player = self.game.get_player(session_id)
        if player is None:
            player = self.game.add_player(session_id)

        self.session_id = session_id

        # Send that someone joined
        # self.broadcast_text("{id} joined.".format(id=session_id))

        self.send_obj(Session(session_id, color=player.color))

        # Add client to the clients list
        self.participants.add(self)

        #periodic = ioloop.PeriodicCallback(self.send_state, 50)
        #periodic.start()

    def on_message(self, text):
        message = json_decode(text)
        session = message.get('session', None);

        if message['action'] == 'hello':
            chatroom = message['body'].get('chatroom', '')
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)

            if chatroom:
                block_id = chatroom
            else:
                block_id = self.game.get_block_id(latitude, longitude)

            if block_id not in self.rooms.keys():
                self.rooms[block_id] = set()
            if block_id not in self.sessions.keys():
                self.sessions[block_id] = set()

            self.rooms[block_id].add(self)
            self.sessions[block_id].add(session)
            self.block_id = block_id

            self.send_obj(Block(block_id))
            online = OnlineUsers(len(self.sessions.get(block_id, () )))
            self.broadcast_obj(online, self.rooms.get(block_id, () ))

        if message['action'] == 'get_spiels':
            chatroom = message['body'].get('chatroom', '')
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)
            since = message['body'].get('since', 0)

            if chatroom:
                block_id = chatroom
                spiels = self.game.get_spiels_by_block_id(block_id)
            else:
                block_id = self.game.get_block_id(latitude, longitude)
                spiels = self.game.get_spiels_by_block_id(block_id, since)
            self.block_id = block_id

            for spiel in spiels:
                self.send_obj(spiel)


        if message['action'] == 'post_spiel':
            name = message['body']['name']
            spiel = message['body']['spiel']
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)
            chatroom = message['body'].get('chatroom', '')

            if spiel:
                date = unix_now_ms()
                if chatroom:
                    block_id = chatroom
                elif latitude and longitude:
                    block_id = self.game.get_block_id(latitude, longitude)

                player = self.game.get_player(session)
                color = player.color

                spiel_dto = Spiel(name=name, spiel=spiel, latitude=latitude, longitude=longitude, date=date, color=color)
                self.notify_recipients(block_id, spiel_dto)
                self.game.post_spiel_to_block(block_id, spiel_dto)

    def on_close(self):
        session_id = self.session_id
        block_id = self.block_id
        # Remove client from the clients list and broadcast leave message
        # self.game.remove_player(session_id)
        self.participants.remove(self)

        self.rooms.get(block_id, () ).remove(self)
        self.sessions.get(block_id, () ).remove(session_id)

        online = OnlineUsers(len(self.sessions.get(block_id, () )))
        self.broadcast_obj(online, self.rooms.get(block_id, () ))
        # self.broadcast_text("{id} left.".format(id=session_id))

    def debug(self, log):
        print log

    def response(self, dto):
        return Response(action=dto._action, body=dto).json()

    def send_obj(self, dto):
        self.send(self.response(dto))

    def notify_recipients(self, block_id, spiel):
        recipients = self.rooms[block_id]
        self.broadcast(recipients, self.response(spiel))

    def broadcast_text(self, text):
        json_message = json_encode({'action': 'log', 'body': {'message': text}})
        self.broadcast(self.participants, json_message)

    def broadcast_obj(self, dto, recipients):
        self.broadcast(recipients, self.response(dto))

