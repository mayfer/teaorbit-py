#!/usr/bin/env python

from db import History
import simplejson as json

h = History()
keys = h.redis.keys('block:*')
things = []
for key in keys:
    key = key.decode('utf8', 'ignore')[6:]
    spiels = h.get_spiels_by_room_id(key)
    spiel = spiels[0]
    things.append((key, spiel, spiel.date))

things = sorted(things, key=lambda x: x[2])

for thing in things[-50:]:
    print thing[0], thing[1].json()
