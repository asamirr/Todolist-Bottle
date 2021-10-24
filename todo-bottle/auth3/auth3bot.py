import requests
import os
from bottle import Bottle, redirect, request, run
from urllib.parse import urlencode
import json
from beaker.middleware import SessionMiddleware
from uuid import uuid4

from requests.sessions import session

OAUTH_URL = "http://127.0.0.1:9000" # from the server running from proxy_server_3bot.py
REDIRECT_URL = "https://login.threefold.me"


app = Bottle()
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
    res = requests.post(f"{OAUTH_URL}/verify", data={"signedAttempt": data, "state": session.get("state")})
    res.raise_for_status()
    return redirect('http://localhost:8080/task')


def is_auth(func):
    def wrapper(*args):
        session = get_session()
        import pdb; pdb.set_trace()
        if not session.get("authorized","") :
            state = str(uuid4()).replace("-", "")
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
        else:
            func(*args)
    return wrapper


app = SessionMiddleware(app, _session_opts)
if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8787)