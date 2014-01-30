from db import History
h = History()
keys = [ key[6:] for key in h.redis.keys('block:*') ]
for key in keys:
    spiels = h.get_spiels(key)
    last = spiels[-1]
    print key, last
