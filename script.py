# never, i repeat, NEVER include API keys in the code
# sys.argv: 1 - user id, 2 - api token

import requests
import json
import sys

def check_connection():
    return requests.get('https://habitica.com/api/v3/status').json()['data']['status']

