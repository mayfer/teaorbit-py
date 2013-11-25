
from redis import Redis


class History(object):
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379, db=0, password=None, socket_timeout=None, connection_pool=None, charset='utf-8', errors='strict', decode_responses=False, unix_socket_path=None)

    def append(self, spiel):
        pass
