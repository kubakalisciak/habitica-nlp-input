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
    elif 'every' in text or 'daily' in text or 'weekly' in text or 'monthly' in text:
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
    
    # weekly category
    if 'weekly' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('weekly', '')}
    if 'every week' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every week', '')}
    if r'every \d+ days' in text:
        return {'frequency': 'weekly', 'everyX': int(re.search(r'every (\d+) days', text).group(1)), 'text': text.replace(re.search(r'every (\d+) days', text).group(0), '')}

    # weekday category
    if 'every monday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every monday', ''), 'repeat':{'m':True, 't':False, 'w':False, 'th':False, 'f':False, 's':False, 'su':False}}
    if 'every tuesday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every tuesday', ''), 'repeat':{'m':False, 't':True, 'w':False, 'th':False, 'f':False, 's':False, 'su':False}}
    if 'every wednesday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every wednesday', ''), 'repeat':{'m':False, 't':False, 'w':True, 'th':False, 'f':False, 's':False, 'su':False}}
    if 'every thursday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every thursday', ''), 'repeat':{'m':False, 't':False, 'w':False, 'th':True, 'f':False, 's':False, 'su':False}}
    if 'every friday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every friday', ''), 'repeat':{'m':False, 't':False, 'w':False, 'th':False, 'f':True, 's':False, 'su':False}}
    if 'every saturday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every saturday', ''), 'repeat':{'m':False, 't':False, 'w':False, 'th':False, 'f':False, 's':True, 'su':False}}
    if 'every sunday' in text:
        return {'frequency': 'weekly', 'everyX': 1, 'text': text.replace('every sunday', ''), 'repeat':{'m':False, 't':False, 'w':False, 'th':False, 'f':False, 's':False, 'su':True}}

    # monthly category
    if 'monthly' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('monthly', '')}
    if 'every month' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every month', '')}
    if r'every \d+ months' in text:
        return {'frequency': 'monthly', 'everyX': int(re.search(r'every (\d+) months', text).group(1)), 'text': text.replace(re.search(r'every (\d+) months', text).group(0), '')}
    
    # month day category
    if 'every 1st' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 1st', ''), 'daysOfMonth': [1]}
    if 'every 2nd' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 2nd', ''), 'daysOfMonth': [2]}
    if 'every 3rd' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 3rd', ''), 'daysOfMonth': [3]}
    if 'every 4th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 4th', ''), 'daysOfMonth': [4]}
    if 'every 5th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 5th', ''), 'daysOfMonth': [5]}
    if 'every 6th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 6th', ''), 'daysOfMonth': [6]}
    if 'every 7th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 7th', ''), 'daysOfMonth': [7]}
    if 'every 8th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 8th', ''), 'daysOfMonth': [8]}
    if 'every 9th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 9th', ''), 'daysOfMonth': [9]}
    if 'every 10th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 10th', ''), 'daysOfMonth': [10]}
    if 'every 11th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 11th', ''), 'daysOfMonth': [11]}
    if 'every 12th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 12th', ''), 'daysOfMonth': [12]}
    if 'every 13th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 13th', ''), 'daysOfMonth': [13]}
    if 'every 14th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 14th', ''), 'daysOfMonth': [14]}
    if 'every 15th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 15th', ''), 'daysOfMonth': [15]}
    if 'every 16th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 16th', ''), 'daysOfMonth': [16]}
    if 'every 17th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 17th', ''), 'daysOfMonth': [17]}
    if 'every 18th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 18th', ''), 'daysOfMonth': [18]}
    if 'every 19th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 19th', ''), 'daysOfMonth': [19]}
    if 'every 20th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 20th', ''), 'daysOfMonth': [20]}
    if 'every 21st' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 21st', ''), 'daysOfMonth': [21]}
    if 'every 22nd' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 22nd', ''), 'daysOfMonth': [22]}
    if 'every 23rd' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 23rd', ''), 'daysOfMonth': [23]}
    if 'every 24th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 24th', ''), 'daysOfMonth': [24]}
    if 'every 25th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 25th', ''), 'daysOfMonth': [25]}
    if 'every 26th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 26th', ''), 'daysOfMonth': [26]}
    if 'every 27th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 27th', ''), 'daysOfMonth': [27]}
    if 'every 28th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 28th', ''), 'daysOfMonth': [28]}
    if 'every 29th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 29th', ''), 'daysOfMonth': [29]}
    if 'every 30th' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 30th', ''), 'daysOfMonth': [30]}
    if 'every 31st' in text:
        return {'frequency': 'monthly', 'everyX': 1, 'text': text.replace('every 31st', ''), 'daysOfMonth': [31]}

add_task(sys.argv[1], sys.argv[2], input(" >>> "))