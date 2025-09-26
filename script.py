#!/usr/bin/env python3
"""
Habitica Natural Language Task Parser

A command-line tool that converts natural language into Habitica tasks.
Supports todos, habits, dailies, and rewards with smart parsing.

Usage: python habitica_nlp.py <user_id> <api_token>
"""

import requests
import json
import sys
import datetime
import re
from dateparser.search import search_dates
from recurrent import RecurringEvent
from dateutil.rrule import DAILY, WEEKLY, MONTHLY

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python script.py <user_id> <api_token>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    api_token = sys.argv[2]
    
    print("Habitica Natural Language Task Creator")
    print("Type your task naturally (e.g., 'exercise every monday', 'buy groceries tomorrow')")
    
    while True:
        task_text = input("\n>>> ").strip()
        if not task_text:
            continue
        if task_text.lower() in ['quit', 'exit', 'q']:
            break
            
        result = create_task_from_text(user_id, api_token, task_text)
        
        if result["success"]:
            print("✅ Task created successfully!")
            task_data = result["data"]["data"]
            print(f"   📝 {task_data['text']}")
            print(f"   📂 Type: {task_data['type']}")
        else:
            print(f"❌ Error: {result['error']}")

def create_task_from_text(user_id, api_token, text):
    """
    Main function to create a Habitica task from natural language text.
    
    Args:
        user_id (str): Habitica user ID
        api_token (str): Habitica API token
        text (str): Natural language task description
        
    Returns:
        dict: Success status and result data or error message
    """
    if not _check_habitica_connection():
        return {"success": False, "error": "Habitica API unavailable"}
    
    # Parse the text and build the task
    task_data = _build_task_from_text(text)
    
    # Send to Habitica API
    return _send_task_to_habitica(user_id, api_token, task_data)

# =============================================================================
# TASK PARSING FUNCTIONS
# =============================================================================

def _build_task_from_text(text):
    """
    Parse natural language text and build a complete task object.
    
    Args:
        text (str): Natural language task description
        
    Returns:
        dict: Complete task object ready for Habitica API
    """
    # Step 1: Determine what type of task this is
    task_type = _determine_task_type(text)
    
    # Step 2: Build base task object
    task = {"type": task_type}
    
    # Step 3: Add type-specific parsing
    if task_type == "reward":
        _parse_reward_task(task, text)
    elif task_type == "habit":
        _parse_habit_task(task, text)
    elif task_type == "todo":
        _parse_todo_task(task, text)
    elif task_type == "daily":
        _parse_daily_task(task, text)
    
    return task

def _determine_task_type(text):
    """
    Analyze text to determine what type of Habitica task it should be.
    
    Rules:
    - Contains "$" → reward
    - Contains "habit" or "+" or "-" → habit  
    - Contains frequency words → daily
    - Default → todo
    """
    text_lower = text.lower().strip()
    
    if "$" in text:
        return "reward"
    elif any(keyword in text_lower for keyword in ["habit", "+", "-"]):
        return "habit"
    elif any(keyword in text_lower for keyword in ["every", "daily", "weekly", "monthly"]):
        return "daily"
    else:
        return "todo"

# =============================================================================
# TASK TYPE PARSERS
# =============================================================================

def _parse_reward_task(task, text):
    """Parse a reward task - extracts value and clean text."""
    value = _extract_reward_value(text)
    clean_text = text.replace(f"${value}", "").strip() if value else text
    
    task["value"] = int(value) if value else 10  # Default value
    task["text"] = clean_text

def _parse_habit_task(task, text):
    """Parse a habit task - determines up/down buttons and difficulty."""
    # Remove the word "habit" from text
    clean_text = text.replace("habit", "").strip()
    
    # Determine which buttons should be enabled
    has_up = "up" in clean_text or "+" in clean_text
    has_down = "down" in clean_text or "-" in clean_text
    
    # If neither specified, enable both (default behavior)
    if not has_up and not has_down:
        has_up = has_down = True
    
    # Clean up the text
    clean_text = clean_text.replace("up", "").replace("down", "")
    clean_text = clean_text.replace("+", "").replace("-", "").strip()
    
    # Extract difficulty and finalize text
    difficulty, final_text = _extract_difficulty(clean_text)
    
    task["up"] = has_up
    task["down"] = has_down
    task["priority"] = difficulty
    task["text"] = final_text

def _parse_todo_task(task, text):
    """Parse a todo task - extracts due date and difficulty."""
    # replace "monday" with "2025-08-28" to avoid interpreting weekdays as in the past
    text = _replace_weekday_with_date(text)
    # Extract any date information
    date_info = _extract_date_from_text(text)
    
    # Extract difficulty from remaining text
    difficulty, final_text = _extract_difficulty(date_info["text"])
    
    task["text"] = final_text
    task["priority"] = difficulty
    if date_info["date"]:
        task["date"] = date_info["date"]

def _parse_daily_task(task, text):
    """Parse a daily task - extracts frequency pattern and difficulty."""
    # Extract frequency information (most complex part)
    frequency_info = _extract_frequency_pattern(text)
    
    # Extract difficulty from the cleaned text
    difficulty, final_text = _extract_difficulty(frequency_info["text"])
    
    # Build the complete daily task
    task.update(frequency_info)
    task["priority"] = difficulty
    task["text"] = final_text

# =============================================================================
# EXTRACTION UTILITIES
# =============================================================================

def _extract_reward_value(text):
    """Extract dollar amount from reward text (e.g., '$50' → '50')."""
    if "$" not in text:
        return ""
    
    match = re.search(r"\$(\d+)", text)
    return match.group(1) if match else ""

def _extract_difficulty(text):
    """
    Extract difficulty level from text and return clean text.
    
    Supported formats:
    - trivial, !0 → 0.1 (trivial)
    - easy, !1 → 1.0 (easy) 
    - medium, !2 → 1.5 (medium)
    - hard, !3 → 2.0 (hard)
    
    Returns:
        tuple: (difficulty_value, clean_text)
    """
    difficulty_map = {
        ("trivial", "!0"): "0.1",
        ("easy", "!1"): "1",
        ("medium", "!2"): "1.5", 
        ("hard", "!3"): "2",
    }
    
    text_lower = text.lower()
    
    for keywords, difficulty_value in difficulty_map.items():
        for keyword in keywords:
            if keyword in text_lower:
                clean_text = text.replace(keyword, "", 1).strip()
                return difficulty_value, clean_text
    
    # Default to easy if no difficulty specified
    return "1", text

def _extract_date_from_text(text):
    """
    Extract date information from text using smart date parsing.
    
    Examples:
    - "tomorrow" → "2025-08-27"
    - "next friday" → "2025-08-30" 
    - "december 25" → "2025-12-25"
    
    Returns:
        dict: {"date": "YYYY-MM-DD" or "", "text": "remaining text"}
    """
    # Use dateparser with proper settings to avoid timezone issues
    results = search_dates(text, settings={
        'TIMEZONE': 'UTC',
        'RETURN_AS_TIMEZONE_AWARE': False,
        'RELATIVE_BASE': datetime.datetime.now()
        'DATE_ORDER': 'DMY'
    })
    
    if not results:
        return {"date": "", "text": text}
    
    # Take the last (most specific) date found
    date_match, date_obj = results[-1]
    formatted_date = date_obj.strftime("%Y-%m-%d")
    clean_text = text.replace(date_match, "").strip()
    
    return {"date": formatted_date, "text": clean_text}

def _replace_weekday_with_date(text):
    """
    Replace weekday words with their corresponding date.
    
    Examples:
    - "monday" → "2025-08-28"
    - "wednesday" → "2025-08-30"
    
    Returns:
        str: Formatted date string
    """
    # prevents the bug where "monday" in todos shows up in the past sometimes
    today = datetime.datetime.now().date()
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    new_words = []
    for word in text.split():
        word_lower = word.lower()
        if word_lower in weekdays:
            target_weekday = weekdays.index(word_lower)
            days_ahead = (target_weekday - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # always pick next week if it’s today
            next_date = today + datetime.timedelta(days=days_ahead)
            new_words.append(next_date.strftime("%Y-%m-%d"))
        else:
            new_words.append(word)
    
    # Return the whole text joined with spaces
    return " ".join(new_words)

# =============================================================================
# FREQUENCY PARSING (MOST COMPLEX PART)
# =============================================================================

def _extract_frequency_pattern(text):
    """
    Extract frequency pattern from text for daily tasks.
    
    This is the most complex parsing because it needs to handle:
    - "every day", "daily" → daily frequency
    - "every monday" → weekly on mondays
    - "every monday and friday" → weekly on multiple days
    - "every 2 weeks" → weekly with interval
    - "every 15th" → monthly on specific day
    
    Returns:
        dict: Frequency information in Habitica format
    """
    # Try smart parsing first with recurrent library
    smart_result = _try_smart_frequency_parsing(text)
    if smart_result:
        return smart_result
    
    # Fall back to manual pattern matching
    return _manual_frequency_parsing(text)

def _try_smart_frequency_parsing(text):
    """
    Use the recurrent library for intelligent frequency parsing.
    
    This handles complex natural language like "every other tuesday"
    or "twice a week" that simple regex can't handle.
    """
    try:
        parser = RecurringEvent()
        rrule = parser.parse(text.lower())
        
        if rrule:
            return _convert_rrule_to_habitica_format(rrule, text)
            
    except Exception:
        # If smart parsing fails, we'll use manual parsing
        pass
    
    return None

def _convert_rrule_to_habitica_format(rrule, original_text):
    """
    Convert a dateutil rrule object into Habitica's frequency format.
    
    This maps recurrent's output to what Habitica expects in the API.
    """
    frequency = rrule._freq
    interval = rrule._interval or 1
    weekdays = rrule._byweekday
    month_days = rrule._bymonthday
    
    clean_text = _remove_frequency_words_from_text(original_text)
    base_result = {"text": clean_text}
    
    if frequency == DAILY:
        return {
            "frequency": "daily",
            "everyX": interval,
            **base_result
        }
    
    elif frequency == WEEKLY:
        result = {
            "frequency": "weekly",
            "everyX": interval,
            **base_result
        }
        
        # Add specific weekdays if specified
        if weekdays:
            result["repeat"] = _build_weekday_repeat_object(weekdays)
        
        return result
    
    elif frequency == MONTHLY:
        result = {
            "frequency": "monthly", 
            "everyX": interval,
            **base_result
        }
        
        # Add specific days of month if specified  
        if month_days:
            result["daysOfMonth"] = list(month_days)
        
        return result
    
    return None

def _manual_frequency_parsing(text):
    """
    Manual frequency parsing using regex patterns.
    
    This is the fallback when smart parsing fails, using your original
    approach but cleaned up and made more readable.
    """
    text_lower = text.lower().strip()
    
    # Try each pattern in order of specificity
    patterns = [
        (_match_daily_patterns, _build_daily_result),
        (_match_weekly_patterns, _build_weekly_result),
        (_match_monthly_patterns, _build_monthly_result),
        (_match_weekday_patterns, _build_weekday_result),
    ]
    
    for matcher, builder in patterns:
        match_data = matcher(text_lower)
        if match_data:
            result = builder(match_data)
            result["text"] = _remove_frequency_words_from_text(text)
            return result
    
    # Default fallback
    return {
        "frequency": "daily",
        "everyX": 1,
        "text": _remove_frequency_words_from_text(text)
    }

# =============================================================================
# FREQUENCY PATTERN MATCHERS
# =============================================================================

def _match_daily_patterns(text):
    """Match daily frequency patterns like 'every 3 days' or 'daily'."""
    if re.search(r"daily|every day|everyday", text):
        return {"interval": 1}
    
    match = re.search(r"every (\d+) days?", text)
    if match:
        return {"interval": int(match.group(1))}
    
    return None

def _match_weekly_patterns(text):
    """Match weekly frequency patterns like 'every 2 weeks' or 'weekly'."""
    if re.search(r"weekly|every week", text):
        return {"interval": 1}
    
    match = re.search(r"every (\d+) weeks?", text)
    if match:
        return {"interval": int(match.group(1))}
    
    return None

def _match_monthly_patterns(text):
    """Match monthly frequency patterns."""
    if re.search(r"monthly|every month", text):
        return {"interval": 1}
    
    match = re.search(r"every (\d+) months?", text)
    if match:
        return {"interval": int(match.group(1))}
    
    # Match ordinal days like "every 15th"
    match = re.search(r"every (\d+)(?:st|nd|rd|th)", text)
    if match:
        return {"interval": 1, "day": int(match.group(1))}
    
    return None

def _match_weekday_patterns(text):
    """Match specific weekday patterns like 'every monday and friday'."""
    weekday_names = {
        "monday": "m", "tuesday": "t", "wednesday": "w", "thursday": "th",
        "friday": "f", "saturday": "s", "sunday": "su",
        "mon": "m", "tue": "t", "wed": "w", "thu": "th",
        "fri": "f", "sat": "s", "sun": "su"
    }
    
    found_days = []
    for day_name, day_code in weekday_names.items():
        if day_name in text:
            found_days.append(day_code)
    
    if found_days:
        return {"days": found_days}
    
    return None

# =============================================================================
# FREQUENCY RESULT BUILDERS
# =============================================================================

def _build_daily_result(match_data):
    """Build daily frequency result."""
    return {
        "frequency": "daily",
        "everyX": match_data["interval"]
    }

def _build_weekly_result(match_data):
    """Build weekly frequency result."""
    return {
        "frequency": "weekly", 
        "everyX": match_data["interval"]
    }

def _build_monthly_result(match_data):
    """Build monthly frequency result."""
    result = {
        "frequency": "monthly",
        "everyX": match_data["interval"]
    }
    
    if "day" in match_data:
        result["daysOfMonth"] = [match_data["day"]]
    
    return result

def _build_weekday_result(match_data):
    """Build weekday-specific frequency result."""
    repeat = {day: (day in match_data["days"]) 
              for day in ["m", "t", "w", "th", "f", "s", "su"]}
    
    return {
        "frequency": "weekly",
        "everyX": 1,
        "repeat": repeat
    }

def _build_weekday_repeat_object(weekdays):
    """Convert rrule weekdays to Habitica repeat object."""
    habitica_days = {0: "m", 1: "t", 2: "w", 3: "th", 4: "f", 5: "s", 6: "su"}
    repeat = {day: False for day in habitica_days.values()}
    
    for weekday in weekdays:
        day_num = weekday.weekday if hasattr(weekday, 'weekday') else weekday
        if day_num in habitica_days:
            repeat[habitica_days[day_num]] = True
    
    return repeat

def _remove_frequency_words_from_text(text):
    """
    Remove frequency-related words to get clean task description.
    
    This is important because we don't want "exercise every monday"
    to become a task called "exercise every monday" - it should just be "exercise".
    """
    # Define patterns to remove (more precise than word-by-word removal)
    patterns_to_remove = [
        r"\bevery\s+\d+\s+(?:days?|weeks?|months?|years?)\b",
        r"\bevery\s+(?:day|week|month|year)\b", 
        r"\b(?:daily|weekly|monthly|yearly|everyday)\b",
        r"\bevery\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\bevery\s+(?:mon|tue|wed|thu|fri|sat|sun)\b",
        r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        r"\b(?:mon|tue|wed|thu|fri|sat|sun)\b",
        r"\bevery\s+\d+(?:st|nd|rd|th)\b",
        r"\b(?:and|or)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    return re.sub(r"\s+", " ", text).strip()

# =============================================================================
# API COMMUNICATION
# =============================================================================

def _check_habitica_connection():
    """Check if Habitica API is available."""
    try:
        response = requests.get("https://habitica.com/api/v3/status", timeout=5)
        return response.json().get("data", {}).get("status") == "up"
    except Exception:
        return False

def _send_task_to_habitica(user_id, api_token, task_data):
    """Send the built task to Habitica API."""
    endpoint = "https://habitica.com/api/v3/tasks/user"
    headers = {
        "x-api-user": user_id,
        "x-api-key": api_token,
        "Content-Type": "application/json",
        "x-client": f"{user_id}-nlpInput",
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=task_data, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get("success", False):
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": data.get("message", "Unknown API error")}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()