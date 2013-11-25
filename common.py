from datetime import datetime
from uuid import uuid4
import calendar
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

