from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from game import GameState
from common import json_encode, json_decode, unix_now, unix_now_ms
from errors import InvalidMessageError
from messages import DTO, Response, Spiel, Session, Block, OnlineUsers, Spiels, Ping, User, KeepAlive, Version
from messages import HelloCM, StillOnlineCM, GetSpielsCM, PostSpielCM, PostPrivateSpielCM

class Connection(SockJSConnection):
    participants = set()
    rooms = {}
    sessions = {}
    game = GameState()

    client_messages = {
        'hello': HelloCM,
        'still_online': StillOnlineCM,
        'get_spiels': GetSpielsCM,
        'post_spiel': PostSpielCM,
    }

    def on_open(self, info):
        if 'session' in info.cookies:
            self.session_id = info.cookies['session'].value
        else:
            self.session_id = self.session.session_id

        # update online count every minute
        periodic = ioloop.PeriodicCallback(self.update_online, 60000)
        periodic.start()

    def _parse_message(self, json_message):
        message_dict = json_decode(json_message)
        if 'action' not in message_dict.keys():
            raise InvalidMessageError

        action = message_dict['action']
        message = self.client_messages[action](message_dict['body'])
        return message

    def on_message(self, text):
        message = self._parse_message(text)

        if message.__class__ == HelloCM:
            self.add_online(connection=self, room_id=message.room_id, session_id=self.session_id, name=message.name)
            self.send_obj(Version())

        if message.__class__ == StillOnlineCM:
            self.sessions.setdefault(message.room_id, {}).setdefault(self.session_id, {})['last_active'] = unix_now_ms()
            ack_dto = KeepAlive()
            self.send_obj(ack_dto)

        if message.__class__ == GetSpielsCM:
            spiels = self.game.get_spiels_by_room_id(message.room_id, since=message.since, until=message.until)

            spiels_dto = Spiels(spiels)
            self.send_obj(spiels_dto)

        if message.__class__ == PostSpielCM:
            if message.spiel:
                date = unix_now_ms()
                player = self.game.get_player(self.session_id)
                color = player.color

                spiel_dto = Spiel(name=message.name, spiel=message.spiel, latitude=message.latitude, longitude=message.longitude, date=date, color=color)
                self.notify_recipients(message.room_id, spiel_dto)
                self.game.post_spiel_to_room(message.room_id, spiel_dto)

                self._update_name(message.name)

        if message.__class__ == PostPrivateSpielCM:
            if message.spiel:
                date = unix_now_ms()
                player = self.game.get_player(self.session_id)
                color = player.color

                spiel_dto = Spiel(name=message.name, spiel=message.spiel, latitude=message.latitude, longitude=message.longitude, date=date, color=color)
                self.notify_recipient(message.to_id, spiel_dto)
                self.game.post_private_spiel(message.to_id, spiel_dto)

    def _update_name(self, name):
        prev_name = self.sessions[self.room_id][self.session_id].get('name', '')
        if name != prev_name:
            self.sessions[self.room_id][self.session_id]['name'] = name
            # and then notify everyone of new name
            self.broadcast_online_users(self.room_id)

    def add_online(self, connection, room_id, session_id, name=''):
        self.room_id = room_id
        self.participants.add(self)

        player = self.game.get_player(self.session_id)
        if player is None:
            player = self.game.add_player(self.session_id)

        self.send_obj(Session(self.session_id, color=player.color))

        if room_id not in self.rooms.keys():
            self.rooms[room_id] = set()
        if room_id not in self.sessions.keys():
            self.sessions[room_id] = {}

        self.rooms[room_id].add(self)

        last_active = unix_now_ms()
        self.sessions[room_id][session_id] = {
            'last_active': last_active,
            'name': name,
            'color': player.color,
        }

        self.send_obj(Block(room_id))

        self.broadcast_online_users(room_id)

    def remove_online(self, room_id, session_id, connection):
        try:
            self.participants.remove(connection)
        except:
            pass
        try:
            self.rooms.get(room_id, () ).remove(connection)
        except:
            pass
        self.sessions[room_id].pop(session_id, None)
        self.broadcast_online_users(room_id)

    def update_online(self):
        # ping = Ping()
        # self.send_obj(ping)
        allowed_inactive = 120000
        now = unix_now_ms()
        for room_id, sess in self.sessions.items():
            for session_id, details in sess.items():
                if details.get('last_active', 0) < now - allowed_inactive:
                    self.remove_online(room_id, session_id, self)

    def broadcast_online_users(self, room_id):
        users = [ User(color=user['color'], name=user['name']) for user in self.sessions.get(room_id, {} ).values() ]
        online = OnlineUsers(len(users), users)
        self.broadcast_obj(online, self.rooms.get(room_id, () ))

    def on_close(self):
        session_id = self.session_id
        room_id = self.room_id
        self.remove_online(room_id=room_id, session_id=session_id, connection=self)
        self.broadcast_online_users(room_id)

    def debug(self, log):
        print log

    def response(self, dto):
        return Response(action=dto._action, body=dto).json()

    def send_obj(self, dto):
        self.send(self.response(dto))

    def notify_recipients(self, room_id, spiel):
        recipients = self.rooms[room_id]
        self.broadcast(recipients, self.response(spiel))

    def broadcast_text(self, text):
        json_message = json_encode({'action': 'log', 'body': {'message': text}})
        self.broadcast(self.participants, json_message)

    def broadcast_obj(self, dto, recipients):
        self.broadcast(recipients, self.response(dto))

