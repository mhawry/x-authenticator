import base64
import hashlib
import os
import re
import json
import redis
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session

AUTH_URL = 'https://twitter.com/i/oauth2/authorize'
TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
REDIRECT_URI = 'http://127.0.0.1:5000/oauth/callback'

SCOPES = ['tweet.read', 'users.read', 'tweet.write', 'offline.access']

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')


def make_token() -> OAuth2Session:
    return OAuth2Session(client_id, redirect_uri=REDIRECT_URI, scope=SCOPES)


code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode('utf-8')
code_verifier = re.sub('[^a-zA-Z0-9]+', '', code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
code_challenge = code_challenge.replace('=', '')

app = Flask(__name__)
app.secret_key = os.urandom(50)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

twitter = make_token()


@app.route('/')
def demo():
    authorization_url, state = twitter.authorization_url(
        AUTH_URL, code_challenge=code_challenge, code_challenge_method='S256'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route('/oauth/callback', methods=['GET'])
def callback():
    code = request.args.get('code')

    token = twitter.fetch_token(
        token_url=TOKEN_URL,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )

    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    r.set('token', j_token)

    return j_token


if __name__ == '__main__':
    app.run()
