# never, i repeat, NEVER include API keys in the code
# sys.argv: 1 - user id, 2 - api token

import requests
import json
import sys
import datetime
from dateparser.search import search_dates
import re

def check_connection():
    return requests.get('https://habitica.com/api/v3/status').json()['data']['status'] == 'up'


def add_task(user_id, api_token, task):
    if check_connection():
        endpoint = 'https://habitica.com/api/v3/tasks/user'
        headers = {'x-api-user': user_id,
                'x-api-key': api_token,
                'Content-Type': 'application/json',
                'x-client': f'{user_id}-nlpInput'}
        payload = {}
        task_type, text = extract_task_type(task)
        payload['type'] = task_type
        if task_type == 'reward':
            payload['value'] = extract_reward_value(text)
            payload['text'] = text.replace(f"${payload['value']}", '')
        elif task_type == 'habit':
            result = extract_habit_up_down(text)
            payload['up'] = result['up']
            payload['down'] = result['down']
            difficulty, text = extract_difficulty(text)
            payload['priority'] = difficulty
            payload['text'] = text
        elif task_type == 'task':
            result = extract_date(text)
            payload['text'] = result['text']
            payload['date'] = result['date']
            difficulty, text = extract_difficulty(text)
            payload['priority'] = difficulty
            payload['text'] = text
        elif task_type == 'daily':
            result = extract_frequency(text)
            difficulty, text = extract_difficulty(text)
            payload['priority'] = difficulty
            payload['text'] = text

        response = requests.post(endpoint, headers=headers, json=payload)
        print(json.dumps(response.json(), indent=4))
        if response.json()['success']:
            print(f"{response.json()['data']['type']} {response.json()['data']['id']} created successfully")
        else:
            print("failed to create task")
    else:
        print("habitica API unavailable")


def extract_task_type(text):
    if '$' in text:
        return ['reward', text]
    elif 'habit' in text:
        return ['habit', text.replace('habit', '')]
    elif 'every' in text or 'daily' in text or 'weekly' in text or 'monthly' in text or 'yearly' in text:
        return 'daily'
    else:
        return 'todo'


def extract_habit_up_down(text):
    return_content = {}
    if 'up' in text or '+' in text:
        return_content['up'] = True
    else:
        return_content['up'] = False
    if 'down' in text or '-' in text:
        return_content['down'] = True
    else:
        return_content['down'] = False
    return_content['text'] = text.replace('up', '').replace('down', '').replace('+', '').replace('-', '')
    return return_content


def extract_date(text):
    results = search_dates(text)
    if not results: return {'date': '', 'text': text}
    else:
        last_result_tuple = results[-1]
        date = last_result_tuple[1].strftime('%Y-%m-%d')
        new_text = text.replace(last_result_tuple[0], '')
        return {'date': date, 'text': new_text}


def extract_reward_value(text):
    if '$' not in text:
        return ''
    return re.search(r'\$[0-9]+', text).group(0)[1:]


def extract_difficulty(text):
    if 'trivial' in text or '!0' in text:
        return ['0.1', text.replace('trivial', '').replace('!0', '')]
    elif 'easy' in text or '!1' in text:
        return ['1', text.replace('easy', '').replace('!1', '')]
    elif 'medium' in text or '!2' in text:
        return ['1.5', text.replace('medium', '').replace('!2', '')]
    elif 'hard' in text or '!3' in text:
        return ['2', text.replace('hard', '').replace('!3', '')]
    else: # default to easy
        return ['1', text]
def extract_frequency(text):
    # daily category
    if 'daily' in text:
        return {'frequency': 'daily', 'everyX': 1, 'text': text.replace('daily', '')}
    if 'every day' in text:
        return {'frequency': 'daily', 'everyX': 1, 'text': text.replace('every day', '')}
    if 'everyday' in text:
        return {'frequency': 'daily', 'everyX': 1, 'text': text.replace('everyday', '')}
    if r'every \d+ days' in text:
        return {'frequency': 'daily', 'everyX': int(re.search(r'every (\d+) days', text).group(1)), 'text': text.replace(re.search(r'every (\d+) days', text).group(0), '')}
    
    
add_task(sys.argv[1], sys.argv[2], input(" >>> "))