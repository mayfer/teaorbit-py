import simplejson as json
from common import json_encode, json_decode
from decimal import Decimal
from geo import Geo
import config

def recursive_json(obj):
    def serialize(obj):
        # recursively walk object's hierarchy
        if isinstance(obj, (bool, int, long, float, basestring)) or obj is None:
            return obj
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, dict):
            obj = obj.copy()
            for key in obj:
                obj[key] = serialize(obj[key])
            return obj
        elif isinstance(obj, list):
            return [serialize(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(serialize([item for item in obj]))
        elif hasattr(obj, '__dict__'):
            # filter private attrs
            return serialize(dict([(key, val) for key, val in obj.__dict__.items() if not key.startswith('_')]))
        else:
            return repr(obj) # convert to string
    return json_encode(serialize(obj))


# data transfer object. defines attributes and serializes to json.
class DTO(object):
    def json(self):
        return recursive_json(self)

    @classmethod
    def from_json(cls, json_text):
        kwargs = json_decode(json_text)
        return cls(**kwargs)

class Ping(DTO):
    _action = 'ping'

    def __init__(self):
        pass

class Response(DTO):
    def __init__(self, action=None, body=None, errors=None):
        self.action = action
        self.body = body
        self.errors = errors

class Session(DTO):
    _action = 'session'

    def __init__(self, session_id, color):
        self.session_id = session_id
        self.color = color

class Version(DTO):
    _action = 'version'

    def __init__(self):
        self.version = config.version

class Spiel(DTO):
    _action = 'new_spiel'

    def __init__(self, name='', spiel='', latitude=49.15, longitude=123.88, date=None, color=None):
        self.name = name
        self.spiel = spiel
        self.date = date
        self.color = color
        self._latitude = latitude
        self._longitude = longitude

class Spiels(DTO):
    _action = 'spiels'

    def __init__(self, spiels=[]):
        self.spiels = spiels

class Block(DTO):
    _action = 'block'

    def __init__(self, block_id):
        self.block_id = block_id

class User(DTO):
    _action = 'user'

    def __init__(self, color, name):
        self.color = color
        self.name = name

class OnlineUsers(DTO):
    _action = 'online'

    def __init__(self, num_online, users):
        self.num_online = num_online
        self.users = users

class KeepAlive(DTO):
    _action = 'keep_alive'

    def __init__(self):
        self.version = config.version

class ClientMessage(DTO):
    def __init__(self, body):
        self.chatroom = body.get('chatroom', '')
        self.latitude = body.get('latitude', 0)
        self.longitude = body.get('longitude', 0)

        if self.chatroom:
            self.room_id = self.chatroom
        else:
            self.room_id = Geo.get_room_id(self.latitude, self.longitude)

class HelloCM(ClientMessage):
    def __init__(self, body):
        super(HelloCM, self).__init__(body)
        self.name = body.get('name', '')

class StillOnlineCM(ClientMessage):
    def __init__(self, body):
        super(StillOnlineCM, self).__init__(body)
        self.name = body.get('name', '')

class GetSpielsCM(ClientMessage):
    def __init__(self, body):
        super(GetSpielsCM, self).__init__(body)
        self.since = body.get('since', None)
        self.until = body.get('until', None)

class PostSpielCM(ClientMessage):
    def __init__(self, body):
        super(PostSpielCM, self).__init__(body)
        self.name = body.get('name', '')
        self.spiel = body.get('spiel', '')

class PostPrivateSpielCM(ClientMessage):
    def __init__(self, body):
        super(PostSpielCM, self).__init__(body)
        self.name = body.get('name', '')
        self.spiel = body.get('spiel', '')
        self.to = body.get('to', '')

