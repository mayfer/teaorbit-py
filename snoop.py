#!/usr/bin/env python

from db import History
import simplejson as json

h = History()
keys = [ key.encode('utf-8')[6:] for key in h.redis.keys('block:*') ]
things = []
for key in keys:
    spiels = h.get_spiels(key)
    last = spiels[-1]
    spiel = json.loads(last)
    things.append((key, last, spiel['date']))

things = sorted(things, key=lambda x: x[2])

for thing in things[-20:]:
    print thing[0], thing[1]
