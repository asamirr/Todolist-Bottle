import nacl.encoding
import nacl.exceptions
import nacl.signing
import requests
import json
import base64

from bottle import Bottle, request, abort, response
from nacl.public import Box


PUBKEY_URL = "/pubkey"
VERIFY_URL = "/verify"
KEY_PATH = "/opt/priv.key"


with open(KEY_PATH) as kp:
    PRIV_KEY = nacl.signing.SigningKey(kp.read(), encoder=nacl.encoding.Base64Encoder)

app = application = Bottle()


def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS, DELETE"
        response.headers[
            "Access-Control-Allow-Headers"
        ] = "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"

        return fn(*args, **kwargs)

    return _enable_cors


@app.route("/checks/readiness")
def readiness():
    with open("/opt/priv.key", "r") as f:
        priv_key = f.read()
    if priv_key:
        return {"readiness": "success"}
    else:
        return abort(400, "Private key not created")


@app.route("/checks/liveness")
def liveness():
    return {"liveness": "success"}


@app.route(PUBKEY_URL)
@enable_cors
def pubkey():
    public_key = PRIV_KEY.verify_key

    return {"publickey": public_key.to_curve25519_public_key().encode(encoder=nacl.encoding.Base64Encoder).decode()}


@app.post(VERIFY_URL)
@enable_cors
def verify():

    is_json = "application/json" in request.headers["Content-Type"]
    if is_json:
        request_data = request.json
    else:
        request_data = request.params

    data = request_data.get("signedAttempt")
    state = request_data.get("state")

    if not data:
        return abort(400, "signedAttempt parameter is missing")

    if not is_json:
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return abort(400, "signedAttempt not in correct format")

    if "signedAttempt" not in data:
        return abort(400, "signedAttempt value is missing")

    username = data.get("doubleName")

    if not username:
        return abort(400, "DoubleName is missing")

    res = requests.get(f"https://login.threefold.me/api/users/{username}", {"Content-Type": "application/json"})
    if res.status_code != 200:
        return abort(400, "Error getting user pub key")

    pub_key = nacl.signing.VerifyKey(res.json()["publicKey"], encoder=nacl.encoding.Base64Encoder)

    # verify data
    signedData = data["signedAttempt"]

    verifiedData = pub_key.verify(base64.b64decode(signedData)).decode()

    data = json.loads(verifiedData)

    if "doubleName" not in data:
        return abort(400, "Decrypted data does not contain (doubleName)")

    if "signedState" not in data:
        return abort(400, "Decrypted data does not contain (state)")

    if data["doubleName"] != username:
        return abort(400, "username mismatch!")

    # verify state
    signed_state = data.get("signedState", "")
    if state != signed_state:
        return abort(400, "Invalid state. not matching one in user session")

    nonce = base64.b64decode(data["data"]["nonce"])
    ciphertext = base64.b64decode(data["data"]["ciphertext"])

    try:
        box = Box(PRIV_KEY.to_curve25519_private_key(), pub_key.to_curve25519_public_key())
        decrypted = box.decrypt(ciphertext, nonce)
    except nacl.exceptions.CryptoError:
        return abort(400, "Error decrypting data")

    try:
        result = json.loads(decrypted)
    except json.JSONDecodeError:
        return abort(400, "3bot login returned faulty data")

    if "email" not in result:
        return abort(400, "Email is not present in data")

    email = result["email"]["email"]

    sei = result["email"]["sei"]
    res = requests.post(
        "https://openkyc.live/verification/verify-sei",
        headers={"Content-Type": "application/json"},
        json={"signedEmailIdentifier": sei},
    )

    if res.status_code != 200:
        return abort(400, "Email is not verified")

    return {"email": email, "username": username}


if __name__ == "__main__":
    app.run(port=9000)
