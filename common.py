import simplejson as json

def json_encode(dictobj):
    return json.dumps(dictobj)

def json_decode(text):
    return json.loads(text)
