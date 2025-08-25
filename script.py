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
        processed_data = process_input(task)
        endpoint = 'https://habitica.com/api/v3/tasks/user'
        headers = {'x-api-user': user_id,
                'x-api-key': api_token,
                'Content-Type': 'application/json',
                'x-client': f'{user_id}-nlpInput'}
        payload = {'text': processed_data['text'],
                'type': 'todo',
                'date': processed_data['date']}
        response = requests.post(endpoint, headers=headers, json=payload)
        print(json.dumps(response.json(), indent=4))
        if response.json()['success']:
            print(f"task {response.json()['data']['id']} created succesfully")
        else:
            print("failed to create task")
    else:
        print("habitica API unavailable")


def process_input(text):
    date_parse_result = extract_date(text)
    return {'text': date_parse_result['text'], 'date': date_parse_result['date']}


def extract_date(text):
    results = search_dates(text)
    if not results: return {'date': '', 'text': text}
    else:
        last_result_tuple = results[-1]
        date = last_result_tuple[1].strftime('%Y-%m-%d')
        new_text = text.replace(last_result_tuple[0], '')
        return {'date': date, 'text': new_text}


add_task(sys.argv[1], sys.argv[2], input(" >>> "))