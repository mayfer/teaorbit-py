from datetime import datetime
from uuid import uuid4
import calendar
import time
import simplejson as json
from pytz import utc

def json_encode(dictobj):
    return json.dumps(dictobj, indent=4).encode('utf-8')

def json_decode(text):
    return json.loads(text)

def datetime_to_unix(date):
    if date is None:
        return 0
    else:
        return calendar.timegm(date.utctimetuple())

def unix_to_datetime(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp).replace(tzinfo=utc)

def unix_now():
    # return UTC Unix timestamp
    return datetime_to_unix(datetime.utcnow().replace(tzinfo=utc))

def datetime_now():
    return datetime.utcnow().replace(tzinfo=utc)

def unix_now_ms():
    date = datetime_now()
    return time.mktime(date.utctimetuple())*1e3 + date.microsecond/1e3
