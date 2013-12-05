import simplejson as json
from common import json_encode, json_decode
from decimal import Decimal

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
class DTO:
    def json(self):
        return recursive_json(self)

    @classmethod
    def from_json(cls, json_text):
        kwargs = json_decode(json_text)
        return cls(**kwargs)

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

class Spiel(DTO):
    _action = 'new_spiel'

    def __init__(self, name='', spiel='', latitude=49.15, longitude=123.88, date=None, color=None):
        self.name = name
        self.spiel = spiel
        self.date = date
        self.color = color
        self._latitude = latitude
        self._longitude = longitude

class Block(DTO):
    _action = 'block'

    def __init__(self, block_id):
        self.block_id = block_id

class OnlineUsers(DTO):
    _action = 'online'

    def __init__(self, num_online):
        self.num_online = num_online
