# never, I repeat, NEVER include API keys in the code
# sys.argv: 1 - user id, 2 - api token
import requests
import json
import sys
import datetime
from dateparser.search import search_dates
import re

def check_connection():
    try:
        res = requests.get("https://habitica.com/api/v3/status")
        return res.json().get("data", {}).get("status") == "up"
    except Exception:
        return False

def add_task(user_id, api_token, task):
    if not check_connection():
        return {"success": False, "error": "Habitica API unavailable"}
    
    endpoint = "https://habitica.com/api/v3/tasks/user"
    headers = {
        "x-api-user": user_id,
        "x-api-key": api_token,
        "Content-Type": "application/json",
        "x-client": f"{user_id}-nlpInput",
    }
    
    payload = {}
    task_type, text = extract_task_type(task)
    payload["type"] = task_type
    
    if task_type == "reward":
        payload["value"] = extract_reward_value(text)
        payload["text"] = text.replace(f"${payload['value']}", "").strip()
    elif task_type == "habit":
        result = extract_habit_up_down(text)
        payload["up"] = result["up"]
        payload["down"] = result["down"]
        difficulty, clean_text = extract_difficulty(result["text"])
        payload["priority"] = difficulty
        payload["text"] = clean_text.strip()
    elif task_type == "todo":
        result = extract_date(text)
        payload["text"] = result["text"].strip()
        if result["date"]:
            payload["date"] = result["date"]
        difficulty, clean_text = extract_difficulty(payload["text"])
        payload["priority"] = difficulty
        payload["text"] = clean_text.strip()
    elif task_type == "daily":
        freq = extract_frequency(text)
        payload.update(freq)
        difficulty, clean_text = extract_difficulty(freq["text"])
        payload["priority"] = difficulty
        payload["text"] = clean_text.strip()
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        
        if data.get("success", False):
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": data.get("message", "Unknown API error")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_task_type(text):
    text = text.lower().strip()
    if "$" in text:
        return ("reward", text)
    elif "habit" in text or '+' in text or '-' in text:
        return ("habit", text.replace("habit", "").strip())
    elif any(word in text for word in ["every", "daily", "weekly", "monthly"]):
        return ("daily", text)
    else:
        return ("todo", text)

def extract_habit_up_down(text):
    return_content = {"up": False, "down": False}
    
    if "up" in text or "+" in text:
        return_content["up"] = True
    if "down" in text or "-" in text:
        return_content["down"] = True
    
    # If neither up nor down is specified, default to both
    if not return_content["up"] and not return_content["down"]:
        return_content["up"] = True
        return_content["down"] = True
    
    clean_text = text.replace("up", "").replace("down", "").replace("+", "").replace("-", "")
    return_content["text"] = clean_text.strip()
    return return_content

def extract_date(text):
    results = search_dates(text, settings={
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': False,
        'RELATIVE_BASE': datetime.datetime.now()
    })
    if not results:
        return {"date": "", "text": text}
    else:
        last_result_tuple = results[-1]
        date = last_result_tuple[1].strftime("%Y-%m-%d")
        new_text = text.replace(last_result_tuple[0], "")
        return {"date": date, "text": new_text}

def extract_reward_value(text):
    if "$" not in text:
        return ""
    match = re.search(r"\$([0-9]+)", text)
    return match.group(1) if match else ""

def extract_difficulty(text):
    mapping = {
        ("trivial", "!0"): "0.1",
        ("easy", "!1"): "1",
        ("medium", "!2"): "1.5",
        ("hard", "!3"): "2",
    }
    
    for keys, val in mapping.items():
        for key in keys:
            if key in text:
                return (val, text.replace(key, ""))
    return ("1", text)  # default easy

def extract_frequency(text):
    text = text.lower().strip()
    
    # daily patterns
    match = re.search(r"every (\d+) days", text)
    if "daily" in text or "every day" in text or "everyday" in text:
        return {"frequency": "daily", "everyX": 1, "text": text.replace("daily", "").replace("every day", "").replace("everyday", "")}
    if match:
        return {"frequency": "daily", "everyX": int(match.group(1)), "text": text.replace(match.group(0), "")}
    
    # weekly patterns
    match = re.search(r"every (\d+) weeks?", text)
    if "weekly" in text or "every week" in text:
        return {"frequency": "weekly", "everyX": 1, "text": text.replace("weekly", "").replace("every week", "")}
    if match:
        return {"frequency": "weekly", "everyX": int(match.group(1)), "text": text.replace(match.group(0), "")}
    
    # specific weekdays
    weekdays = {
        "monday": "m", "tuesday": "t", "wednesday": "w", "thursday": "th",
        "friday": "f", "saturday": "s", "sunday": "su"
    }
    for day, code in weekdays.items():
        if f"every {day}" in text:
            clean = text.replace(f"every {day}", "")
            repeat = {k: (k == code) for k in ["m", "t", "w", "th", "f", "s", "su"]}
            return {"frequency": "weekly", "everyX": 1, "text": clean, "repeat": repeat}
    
    # monthly patterns
    match = re.search(r"every (\d+) months?", text)  # Fixed: \d+ not d+
    if "monthly" in text or "every month" in text:
        return {"frequency": "monthly", "everyX": 1, "text": text.replace("monthly", "").replace("every month", "")}
    if match:
        return {"frequency": "monthly", "everyX": int(match.group(1)), "text": text.replace(match.group(0), "")}
    
    # day of month
    match = re.search(r"every (\d+)(st|nd|rd|th)", text)  # Fixed: \d+ not d+
    if match:
        day = int(match.group(1))
        return {"frequency": "monthly", "everyX": 1, "text": text.replace(match.group(0), ""), "daysOfMonth": [day]}
    
    return {"frequency": "daily", "everyX": 1, "text": text}  # fallback

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <user_id> <api_token>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    api_token = sys.argv[2]
    
    task_text = input(" >>> ")
    result = add_task(user_id, api_token, task_text)
    
    if result.get("success"):
        print("Task added successfully!")
        print(json.dumps(result.get("data"), indent=4))
    else:
        print(f"Error: {result.get('error')}")