# never, i repeat, NEVER include API keys in the code
# sys.argv: 1 - user id, 2 - api token

import requests
import json
import sys
import datetime
from dateparser.search import search_dates

def check_connection():
    return requests.get('https://habitica.com/api/v3/status').json()['data']['status'] == 'up'


def add_task(user_id, api_token, task):
    if check_connection():
        endpoint = 'https://habitica.com/api/v3/tasks/user'
        headers = {'x-api-user': user_id,
                'x-api-key': api_token,
                'Content-Type': 'application/json',
                'x-client': f'{user_id}-nlpInput'}
        payload = {'text': task,
                'type': 'todo'}
        response = requests.post(endpoint, headers=headers, json=payload)
        print(json.dumps(response.json(), indent=4))
        if response.json()['success']:
            print(f"task {response.json()['data']['id']} created succesfully")
        else:
            print("failed to create task")
    else:
        print("habitica API unavailable")


def process_input(text):
    pass


def extract_date(text):
    return search_dates(text)
    # return only the date in the iso format
    # remove the date keyword from the text and return the new text


print(extract_date(input(" >>> ")))
# add_task(sys.argv[1], sys.argv[2], input(" >>> "))