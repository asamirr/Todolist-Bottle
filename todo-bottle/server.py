from bottle import Bottle, request, response, redirect, run
import db
import jsend
import requests
from urllib.parse import urlencode
import json
from beaker.middleware import SessionMiddleware
from uuid import uuid4


# from the server running from proxy_server_3bot.py
OAUTH_URL = "http://127.0.0.1:9000"
REDIRECT_URL = "https://login.threefold.me"


app = Bottle()
db.connect("todo.db")
_session_opts = {"session.type": "file", "session.data_dir": "./data", "session.auto": True}


def get_session():
    return request.environ.get("beaker.session")


@app.route("/start")
def start():
    state = str(uuid4()).replace("-", "")
    session = get_session()
    session["state"] = state
    res = requests.get(f"{OAUTH_URL}/pubkey")
    res.raise_for_status()
    data = res.json()
    params = {
        "state": state,
        "appid": request.get_header("host"),
        "scope": json.dumps({"user": True, "email": True}),
        "redirecturl": "/callback",
        "publickey": data["publickey"].encode(),
    }
    params = urlencode(params)
    return redirect(f"{REDIRECT_URL}?{params}", code=302)


@app.route("/callback")
def callback():
    session = get_session()
    data = request.query.get("signedAttempt")
    res = requests.post(f"{OAUTH_URL}/verify", 
                        data={"signedAttempt": data, "state": session.get("state")})
    res.raise_for_status()
    session['authorized'] = True
    return redirect('http://localhost:8080/')


def is_auth(func):
    def wrapper(*args):
        session = get_session()
        if not session.get("authorized", ""):
            return redirect(f"http://localhost:8000/start", code=302)
        else:
            return func(*args)
    return wrapper


_allow_origin = '*'
_allow_methods = 'PUT, GET, POST, DELETE, OPTIONS'
_allow_headers = 'Authorization, Origin, Accept, Content-Type, X-Requested-With'

@app.hook('after_request')
def enable_cors():
    '''Add headers to enable CORS'''
    response.headers['Access-Control-Allow-Origin'] = _allow_origin
    response.headers['Access-Control-Allow-Methods'] = _allow_methods
    response.headers['Access-Control-Allow-Headers'] = _allow_headers

@app.route('/', method='OPTIONS')
@app.route('/<path:path>', method='OPTIONS')
def options_handler(path=None):
    return


@app.get("/task")
@app.get("/task/<task_id:int>")
@is_auth
def task_get(task_id=None):
    """ Fetch a single task or fetch all tasks.
    :return: jsend JSON object with key 'data' containing a single or a list of tasks
    response 200 OK - response data has content
             404 Not Found - task task_id not found
             500 Server Internal Error - most likely database error
    """
    response.content_type = "application/json"
    response.headers["Cache-Control"] = "no-cache"
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    # response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    try:
        if task_id is None:
            tasks = db.task.select()
            response.status = 200
            return jsend.success([dict(task) for task in tasks])
        else:
            task = db.task.select(task_id)
            if task is None:
                response.status = 404
                return jsend.fail("task {} not found".format(task_id))
            else:
                response.status = 200
                return jsend.success(dict(task))
    except Exception as e:
        response.status = 500
        return jsend.error("GET task failed", code=type(e).__name__, data=str(e))


@app.put("/task")
@app.put("/task/<task_id:int>")
def task_put(task_id=None):
    """ Update a single task. Updating all tasks not supported.
    :return: jsend JSON object with key 'data' containing the task_id of the updated task
    response 200 OK - task updated successfully
             400 no JSON content in request
             404 Not Found - task task_id not found
             405 PUT on collection not supported
             500 Server Internal Error - most likely database error
    """
    response.content_type = "application/json"
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    # response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    try:
        if task_id is None:
            response.status = 405
            return jsend.error("PUT on collection not supported")
        else:
            task = db.task.select(task_id)
            if task is None:
                response.status = 404
                return jsend.fail("task {} not found".format(task_id))
            else:
                data = request.json
                if data is None:
                    response.status = 400
                    return jsend.fail("no JSON content")
                else:
                    db.task.update(task_id, data["summary"], data["description"], data["duedate"], data["status_id"])
                    response.status = 200
                    return jsend.success({"id": task_id})
    except Exception as e:
        response.status = 500
        return jsend.error("PUT task failed", code=type(e).__name__, data=str(e))


@app.post("/task")
@app.post("/task/<task_id:int>")
@is_auth
def task_post(task_id=None):
    """ Insert a new task.
    :return: jsend JSON object with key 'data' containing the task_id of newly created task
    response 201 Created - task inserted
             400 No JSON content in request
             405 insert with predefined task_id not possible
             500 Server Internal Error - most likely database error
    """
    response.content_type = "application/json"
    # response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080/'
    # response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    # response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    try:
        if task_id is None:
            data = request.json
            if data is None:
                response.status = 400
                return jsend.fail("no JSON content")
            else:
                task_id = db.task.insert(data["summary"], data["description"], data["duedate"], data["status_id"])
                response.status = 201
                return jsend.success({"id": task_id})
        else:
            response.status = 405
            return jsend.error("POST on task_id not possible")
    except Exception as e:
        response.status = 500
        return jsend.error("POST task failed", code=type(e).__name__, data=str(e))


@app.delete("/task")
@app.delete("/task/<task_id:int>")
def task_delete(task_id=None):
    """ Delete a single task. Deleting all tasks is not supported.
    :return: jsend JSON object with key 'data' containing the content of the deleted task
    response: 200 OK - task deleted successfully
              404 task task_id not found
              405 delete on collection not supported
              500 Server Internal Error - most likely database error
    """
    response.content_type = "application/json"
    # response.headers['Access-Control-Allow-Origin'] = '*'
    # response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    # response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    try:
        if task_id is None:
            response.status = 405
            return jsend.error("DELETE on collection not supported")
        else:
            task = db.task.select(task_id)
            if task is None:
                response.status = 404
                return jsend.fail("task {} not found".format(task_id))
            else:
                db.task.delete(task_id)
                response.status = 200
                return jsend.success(dict(task))
    except Exception as e:
        response.status = 500
        return jsend.error("DELETE task failed", code=type(e).__name__, data=str(e))


app = SessionMiddleware(app, _session_opts)

if __name__ == "__main__":
    run(app=app, host="0.0.0.0", port=8000)
    # app.app.run(host="0.0.0.0", port=8000, debug=True, reloader=True)
