from redis import Redis
from redis.exceptions import ConnectionError
from messages import SpielView, SessionView
from models import Session, Spiel
from common import datetime_now, datetime_to_unix
from datetime import timedelta
import config

class FakeRedis(object):
    def __init__(self):
        self._blocks = {}

    def zadd(self, room_id, spiel_json, timestamp):
        if room_id not in self._blocks:
            self._blocks[room_id] = []
        self._blocks[room_id].append({'score': timestamp, 'data': spiel_json})

    def zrevrangebyscore(self, room_id, max='+inf', min='-inf', start=None, limit=None, num=None):
        max = max[1:] if max.startswith('(') else max
        min = min[1:] if min.startswith('(') else min
        return [ row['data'] for row in sorted(self._blocks.get(room_id, []), key=lambda d: d['score'], reverse=True) if row['score'] > float(min) and row['score'] < float(max) ]

    def get(self, key):
        return self._blocks.get(key, None)

    def set(self, key, val):
        self._blocks[key] = val

    def delete(self, key):
        del self._blocks[key]

class History(object):
    spiels_per_request = config.spiels_per_request

    def __init__(self):
        try:
            self.redis = Redis(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, unix_socket_path=None)
            # test connection
            self.redis.ping()
        except ConnectionError:
            print "*** [notice] Can't connect to Redis, using a fall-back in-memory database."
            self.redis = FakeRedis()

    def __encode(self, text):
        return text.encode('utf-8')

    def set_player_public_id(self, session_id, public_id):
        key = 'public_id:{p}'.format(p=public_id)
        self.redis.set(key, session_id)

    def get_player_from_public_id(self, public_id):
        key = 'public_id:{p}'.format(p=public_id)
        session_id = self.redis.get(key)
        return self.get_player(session_id)

    def add_player(self, session_id):
        r = lambda: random.randint(0,255)

        player = Session(session_id)

        key = 'player:{s}'.format(s=session_id)
        self.redis.set(key, player.json())

        self.set_player_public_id(session_id, player.public_id)
        return player

    def get_player(self, session_id):
        key = 'player:{s}'.format(s=session_id)
        player_json = self.redis.get(key)
        if player_json is not None:
            player = Session.from_json(player_json)
        else:
            player = None

        return player

    def remove_player(self, session_id):
        key = 'player:{s}'.format(s=session_id)
        self.redis.delete(key)

    def post_spiel(self, room_id, spiel):
        key = "block:{b}".format(b=self.__encode(room_id))
        self.redis.zadd(key, spiel.json(), spiel.date)

    def post_private_spiel(self, to_id, pv_spiel):
        key = "pm:{b}".format(b=self.__encode(to_id))
        self.redis.zadd(key, pv_spiel.json(), pv_spiel.date)

    def get_spiels_by_room_id(self, room_id, since=None, until=None):
        if since is None:
            since = '-inf'

        if until is None:
            until = '+inf'

        # reduce the decimals to proper decimals instead of silly python exponentials
        if since != '-inf' and since != '+inf':
            since = '%f' % since
        if until != '-inf' and until != '+inf':
            until = '%f' % until

        # the brackets mean exclude that exact value
        key = "block:{b}".format(b=self.__encode(room_id))
        spiel_jsons = self.redis.zrevrangebyscore(key, max="({u}".format(u=until), min="({s}".format(s=since), start=0, num=self.spiels_per_request)

        if until is None:
            spiel_jsons.reverse()

        spiels = []
        for spiel_json in spiel_jsons:
            spiel = Spiel.from_json(spiel_json)
            spiels.append(spiel)

        return spiels

