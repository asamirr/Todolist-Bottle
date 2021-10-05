import json
from datetime import date, datetime, time

SUCCESS = "success"
FAIL = "fail"
ERROR = "error"


def success(data=None):
    r = {"status": SUCCESS, "data": data}
    return json.dumps(r, default=json_serialize)


def fail(data=None):
    r = {"status": FAIL, "data": data}
    return json.dumps(r, default=json_serialize)


def error(message=None, code=None, data=None):
    if code is None and data is None:
        r = {"status": ERROR, "message": message}
    elif code is None:
        r = {"status": ERROR, "message": message, "data": data}
    elif data is None:
        r = {"status": ERROR, "message": message, "code": code}
    else:
        r = {"status": ERROR, "message": message, "code": code, "data": data}
    return json.dumps(r, default=json_serialize)


def json_serialize(obj):
    """ JSON serializer for objects not serializable by default by json.dumps. """

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, date):
        return obj.isoformat()

    if isinstance(obj, time):
        return obj.isoformat()

    raise TypeError("Type {} not serializable".format(type(obj)))