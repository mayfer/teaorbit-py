from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from db import History
from common import json_encode, json_decode, unix_now, unix_now_ms
from errors import InvalidMessageError
from messages import DTO, ResponseView, SpielView, SessionView, BlockView, OnlineUsersView, SpielsView, PingView, UserView, KeepAliveView, VersionView
from messages import HelloCM, StillOnlineCM, GetSpielsCM, PostSpielCM, PostPrivateSpielCM
from models import Session, RoomSession
import actions

class Connection(SockJSConnection):
    participants = set()
    connections = {}
    room_sessions = {}
    db = History()

    message_actions = {
        HelloCM: actions.hello,
        StillOnlineCM: actions.still_online,
        GetSpielsCM: actions.get_spiels,
        PostSpielCM: actions.post_spiel,
    }

    def __init__(self, *args, **kwargs):
        self.client_messages = {}
        for msg_class, action in self.message_actions.items():
            self.client_messages[msg_class._action] = msg_class

        super(Connection, self).__init__(*args, **kwargs)

    def on_open(self, info):
        if 'session' in info.cookies:
            self.session_id = info.cookies['session'].value
        else:
            self.session_id = self.session.session_id

        # update online count every minute
        periodic = ioloop.PeriodicCallback(self.update_online, 60000)
        periodic.start()

        self.send_obj(VersionView())

    def on_message(self, text):
        message_dict = json_decode(text)
        if 'action' not in message_dict.keys():
            raise InvalidMessageError

        action = message_dict['action']
        message = self.client_messages[action](message_dict['body'])
        action = self.message_actions[message.__class__]
        return action(self, message)

    def _update_name(self, name):
        try:
            prev_name = self.room_sessions[self.room_id][self.session_id].name

            if name != prev_name:
                self.room_sessions[self.room_id][self.session_id].name = name
                # and then notify everyone of new name
                self.broadcast_online_users(self.room_id)
        except KeyError:
            self.add_online(self, self.room_id, self.session_id, name)

    def add_online(self, connection, room_id, session_id, name='', channels=[]):
        self.room_id = room_id
        self.participants.add(self)

        player = self.db.get_player(self.session_id)
        if player is None:
            player = self.db.add_player(self.session_id)

        self.send_obj(SessionView(self.session_id, color=player.color))

        if room_id not in self.connections.keys():
            self.connections[room_id] = {}
        if session_id not in self.connections[room_id]:
            self.connections[room_id][session_id] = set()
        self.connections[room_id][session_id].add(self)

        if room_id not in self.room_sessions.keys():
            self.room_sessions[room_id] = {}

        last_active = unix_now_ms()

        session = Session(session_id=session_id, color=player.color, last_active=last_active, public_id=player.public_id)
        self.current_session = session

        self.room_sessions[room_id][session_id] = RoomSession(name=name, session=session)

        self.send_obj(BlockView(room_id))

        self.broadcast_online_users(room_id)

    def remove_online(self, room_id, session_id, connection):
        try:
            self.participants.remove(connection)
            self.connections[room_id][session_id].remove(connection)
            if len(self.connections[room_id][session_id]) == 0:
                self.room_sessions[room_id].pop(session_id, None)
        except KeyError as e:
            print "KeyError", e

        self.broadcast_online_users(room_id)

    def update_online(self):
        # ping = PingView()
        # self.send_obj(ping)
        allowed_inactive = 120000
        now = unix_now_ms()
        if hasattr(self, 'current_session'):
            session = self.current_session
            if session.last_active < now - allowed_inactive:
                for conn in self.connections[self.room_id].get(session.session_id, set()).copy():
                    self.remove_online(self.room_id, session.session_id, conn)

    def broadcast_online_users(self, room_id):
        users = [ UserView(color=roomsession.session.color, name=roomsession.name) for roomsession in self.room_sessions[room_id].values() ]
        online = OnlineUsersView(len(users), users)
        connections = self.connections_for_room_id(room_id)
        self.broadcast_obj(online, connections)

    def connections_for_room_id(self, room_id):
        connections = set()
        for conn_set in self.connections.get(room_id, {} ).values():
            for conn in conn_set:
                if conn.room_id == room_id:
                    connections.add(conn)
        return connections

    def on_close(self):
        session_id = self.session_id
        room_id = self.room_id
        self.remove_online(room_id=room_id, session_id=session_id, connection=self)
        self.broadcast_online_users(room_id)

    def debug(self, log):
        print log

    def response(self, dto):
        if hasattr(self, 'room_id'):
            room_id = self.room_id
        else:
            room_id = ''
        return ResponseView(action=dto._action, body=dto, channel=room_id).json()

    def send_obj(self, dto):
        self.send(self.response(dto))

    def notify_recipients(self, room_id, spiel):
        recipients = self.connections_for_room_id(room_id)
        self.broadcast(recipients, self.response(spiel))

    def broadcast_text(self, text):
        json_message = json_encode({'action': 'log', 'body': {'message': text}})
        self.broadcast(self.participants, json_message)

    def broadcast_obj(self, dto, recipients):
        self.broadcast(recipients, self.response(dto))

