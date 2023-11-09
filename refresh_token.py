import os
import json
import main

TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'

twitter = main.make_token()

client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')

t = main.r.get('token')
bb_t = t.replace("'", '"')
data = json.loads(bb_t)

refreshed_token = twitter.refresh_token(
    client_id=client_id,
    client_secret=client_secret,
    token_url=TOKEN_URL,
    refresh_token=data['refresh_token'],
)

st_refreshed_token = '"{}"'.format(refreshed_token)
j_refreshed_token = json.loads(st_refreshed_token)
main.r.set('token', j_refreshed_token)
