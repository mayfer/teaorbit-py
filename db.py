from redis import Redis
from redis.exceptions import ConnectionError
from messages import Spiel, Session
from common import datetime_now, datetime_to_unix
from datetime import timedelta

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
    spiels_per_request = 100

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

    def insert_spiel(self, room_id, spiel_json, timestamp):
        key = "block:{b}".format(b=self.__encode(room_id))
        self.redis.zadd(key, spiel_json, timestamp)

    def insert_spiel(self, to_id, spiel_json, timestamp):
        key = "pm:{b}".format(b=self.__encode(to_id))
        self.redis.zadd(key, spiel_json, timestamp)

    def get_spiels(self, room_id, since=None, until=None):
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

        return spiel_jsons

    def set_player(self, session_id, player):
        key = 'player:{s}'.format(s=session_id)
        self.redis.set(key, player.json())

    def get_player(self, session_id):
        key = 'player:{s}'.format(s=session_id)
        player_json = self.redis.get(key)
        if player_json is not None:
            return Session.from_json(player_json)
        else:
            return None

    def get_session_id_for_alias(self, alias):
        key = 'alias:{s}'.format(s=session_id)
        session_id = self.redis.get(key)
        return session_id

    def remove_player(self, session_id):
        key = 'player:{s}'.format(s=session_id)
        self.redis.delete(key)
