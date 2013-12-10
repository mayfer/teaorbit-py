from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from game import GameState
from common import json_encode, json_decode, unix_now, unix_now_ms
from dto import DTO, Response, Spiel, Session, Block, OnlineUsers, InitialSpiels, Ping

class Connection(SockJSConnection):
    participants = set()
    rooms = {}
    sessions = {}
    game = GameState()

    def on_open(self, info):
        if 'session' in info.cookies:
            self.session_id = info.cookies['session'].value
        else:
            self.session_id = self.session.session_id

        # update online count every minute
        periodic = ioloop.PeriodicCallback(self.update_online, 60000)
        periodic.start()

    def add_online(self, connection, block_id, session_id):
        self.block_id = block_id
        self.participants.add(self)

        player = self.game.get_player(self.session_id)
        if player is None:
            player = self.game.add_player(self.session_id)

        self.send_obj(Session(self.session_id, color=player.color))

        if block_id not in self.rooms.keys():
            self.rooms[block_id] = set()
        if block_id not in self.sessions.keys():
            self.sessions[block_id] = {}

        self.rooms[block_id].add(self)

        last_active = unix_now_ms()
        self.sessions[block_id][session_id] = {
            'last_active': last_active,
            'name': '',
        }

        self.send_obj(Block(block_id))

        self.broadcast_online_count(block_id)

    def remove_online(self, block_id, session_id, connection):
        self.participants.remove(connection)
        self.rooms.get(block_id, () ).remove(connection)
        self.sessions[block_id].pop(session_id, None)

    def update_online(self):
        ping = Ping()
        self.send_obj(ping)
        allowed_inactive = 120000
        now = unix_now_ms()
        for block_id, sess in self.sessions.items():
            for session_id, details in sess.items():
                if details.get('last_active', 0) < now - allowed_inactive:
                    self.remove_online(block_id, session_id, self)

    def broadcast_online_count(self, block_id):
        online = OnlineUsers(len(self.sessions.get(block_id, {} ).keys()))
        self.broadcast_obj(online, self.rooms.get(block_id, () ))

    def on_message(self, text):
        message = json_decode(text)
        # session = message.get('session', None);

        if message['action'] == 'hello':
            chatroom = message['body'].get('chatroom', '')
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)

            if chatroom:
                block_id = chatroom
            else:
                block_id = self.game.get_block_id(latitude, longitude)

            self.add_online(connection=self, block_id=block_id, session_id=self.session_id)

        if message['action'] == 'pong':
            chatroom = message['body'].get('chatroom', '')
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)

            if chatroom:
                block_id = chatroom
            else:
                block_id = self.game.get_block_id(latitude, longitude)

            self.sessions[block_id][self.session_id]['last_active'] = unix_now_ms()

        if message['action'] == 'get_spiels':
            chatroom = message['body'].get('chatroom', '')
            latitude = message['body'].get('latitude', 0)
            longitude = message['body'].get('longitude', 0)
            since = message['body'].get('since', 0)

            if chatroom:
                block_id = chatroom
            else:
                block_id = self.game.get_block_id(latitude, longitude)

            spiels = self.game.get_spiels_by_block_id(block_id, since=since)

            spiels_dto = InitialSpiels(spiels)
            self.send_obj(spiels_dto)
            self.block_id = block_id

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

                player = self.game.get_player(self.session_id)
                color = player.color

                spiel_dto = Spiel(name=name, spiel=spiel, latitude=latitude, longitude=longitude, date=date, color=color)
                self.notify_recipients(block_id, spiel_dto)
                self.game.post_spiel_to_block(block_id, spiel_dto)

                self.sessions[block_id][self.session_id]['name'] = name

    def on_close(self):
        session_id = self.session_id
        block_id = self.block_id
        self.remove_online(block_id=block_id, session_id=session_id, connection=self)
        self.broadcast_online_count(block_id)

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

