from redis import Redis
from dto import Spiel
from common import datetime_now, datetime_to_unix
from datetime import timedelta

class History(object):
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, unix_socket_path=None)

    def insert_spiel(self, block_id, spiel_json, timestamp):
        # spiel_id = self.redis.get last id amk
        self.redis.zadd(block_id, spiel_json, timestamp)

    def get_spiels(self, block_id):
        since = datetime_to_unix(datetime_now() - timedelta(days=2))
        spiel_jsons = self.redis.zrangebyscore(block_id, since, '+inf')
        return spiel_jsons

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
