from redis import Redis
from redis.exceptions import ConnectionError
from dto import Spiel, Session
from common import datetime_now, datetime_to_unix
from datetime import timedelta

class FakeRedis(object):
    def __init__(self):
        self._blocks = {}

    def zadd(self, block_id, spiel_json, timestamp):
        if block_id not in self._blocks:
            self._blocks[block_id] = []
        self._blocks[block_id].append({'score': timestamp, 'data': spiel_json})

    def zrevrangebyscore(self, block_id, since='-inf', until='+inf', start=None, limit=None):
        return [ row['data'] for row in sorted(self._blocks.get(block_id, []), key=lambda d: d['score']) if row['score'] > float(since) and row['score'] < float(until) ]

class History(object):
    def __init__(self):
        try:
            self.redis = Redis(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, unix_socket_path=None)
            # test connection
            self.redis.ping()
        except ConnectionError:
            print "*** [notice] Can't connect to Redis, using a fall-back in-memory database."
            self.redis = FakeRedis()

    def insert_spiel(self, block_id, spiel_json, timestamp):
        # spiel_id = self.redis.get last id amk
        self.redis.zadd("block:{b}".format(b=block_id), spiel_json, timestamp)

    def get_spiels(self, block_id, since):
        # since = datetime_to_unix(datetime_now() - timedelta(days=2))
        spiel_jsons = self.redis.zrevrangebyscore("block:{b}".format(b=block_id), '+inf', since, start=0, num=30)
        spiel_jsons.reverse()
        return spiel_jsons

    def set_player(self, session_id, player):
        self.redis.set('player:{s}'.format(s=session_id), player.json())

    def get_player(self, session_id):
        player_json = self.redis.get('player:{s}'.format(s=session_id))
        if player_json is not None:
            return Session.from_json(player_json)
        else:
            return None

    def remove_player(self, session_id):
        self.redis.delete('player:{s}'.format(s=session_id))
"""

Notes

Add item with score/date
zadd(name1, score1)

Remove date range:
zremrangebyscore(name, min, max)




name = 'myset'
        r.zadd(name, 'one', 1)
        r.zadd(name, 'two', 2)
        r.zadd(name, 'three', 3)
        r.zadd(name, 'four', 4)

        self.assertTrue(r.zrangebyscore(name, '-inf', '+inf') == ['one', 'two', 'three', 'four'])
        self.assertTrue(r.zrangebyscore(name, 1, 1) == ['one'])
        self.assertTrue(r.zrangebyscore(name, 1, 2) == ['one', 'two'])
        self.assertTrue(r.zrangebyscore(name, 2, 3) == ['two', 'three'])
        self.assertTrue(r.zrangebyscore(name, '(1', '(2') == [])
        self.assertTrue(r.zrangebyscore(name, '(1', '(3') == ['two'])



"""
