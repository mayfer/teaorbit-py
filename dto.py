import simplejson as json
from common import json_encode, json_decode
from decimal import Decimal

def recursive_json(obj):
    """Represent instance of a class as JSON.
    Arguments:
    obj -- any object
    Return:
    String that reprent JSON-encoded object.
    """
    def serialize(obj):
        """Recursively walk object's hierarchy."""
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
            return serialize(obj.__dict__)
        else:
            return repr(obj) # convert to string
    return json_encode(serialize(obj))


class DTO:

    def json(self):
        return recursive_json(self)

class Response(DTO):
    def __init__(self, action=None, body=None, errors=None):
        self.action = action
        self.body = body
        self.errors = errors

class Session(DTO):
    _action = 'session'

    def __init__(self, session_id):
        self.session_id = session_id

class Spiel(DTO):
    _action = 'new_spiel'

    def __init__(self, name='', spiel='', latitude=0, longitude=0, date=None):
        self.name = name
        self.spiel = spiel
        self.latitude = latitude
        self.longitude = longitude
        self.date = date

