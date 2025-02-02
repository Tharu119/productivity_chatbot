import json
import os
import time
import threading
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
import dateparser

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

REMINDER_FILE = "reminders.json"

def load_reminders():
    """ Load saved reminders from file """
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, "r") as file:
            return json.load(file)
    return []

def save_reminders(reminders):
    """ Save reminders to file """
    with open(REMINDER_FILE, "w") as file:
        json.dump(reminders, file, indent=4)

def extract_datetime(user_message):
    """
    Extracts date and time from the user message.
    - Fixes '11.29 PM' to '11:29 PM'
    - Supports 'tomorrow', 'next Monday', 'in 2 hours'
    """
    cleaned_message = user_message.lower()

    # Fix incorrect time formats (Replace '.' with ':')
    cleaned_message = re.sub(r"(\d{1,2})\.(\d{2})", r"\1:\2", cleaned_message)

    # Remove unnecessary words
    cleaned_message = re.sub(r"(remind me to|reminder for|at|on)", "", cleaned_message).strip()

    # Extract time using regex
    time_match = re.search(r"\d{1,2}[:]\d{2}\s?(AM|PM|am|pm)?", cleaned_message)
    extracted_time = time_match.group(0) if time_match else ""

    # Remove extracted time from message to get only the task
    task_message = cleaned_message.replace(extracted_time, "").strip()

    now = datetime.now()

    # Handle relative times like "in 2 hours", "in 30 minutes"
    relative_time_match = re.search(r"in (\d+) (minutes|hours|days)", cleaned_message)
    if relative_time_match:
        amount = int(relative_time_match.group(1))
        unit = relative_time_match.group(2)

        if unit == "minutes":
            extracted_datetime = now + timedelta(minutes=amount)
        elif unit == "hours":
            extracted_datetime = now + timedelta(hours=amount)
        elif unit == "days":
            extracted_datetime = now + timedelta(days=amount)
        else:
            extracted_datetime = None
    elif "tomorrow" in cleaned_message:
        extracted_datetime = now + timedelta(days=1)
        extracted_datetime = extracted_datetime.replace(hour=8, minute=0)  # Default to 8 AM if no time is given
    elif "next monday" in cleaned_message:
        days_until_monday = (7 - now.weekday() + 0) % 7 + 1
        extracted_datetime = now + timedelta(days=days_until_monday)
        extracted_datetime = extracted_datetime.replace(hour=8, minute=0)
    else:
        extracted_datetime = dateparser.parse(extracted_time, settings={'PREFER_DATES_FROM': 'future'})

    return extracted_datetime, task_message

@app.route("/")
def index():
    """ Render the chatbot UI """
    return render_template("index.html")

@app.route("/add_reminder", methods=["POST"])
def add_reminder():
    """ Add a reminder with extracted date and time """
    user_message = request.json.get("message", "")

    # Extract datetime
    extracted_datetime, task_message = extract_datetime(user_message)

    if not extracted_datetime:
        return jsonify({"response": "I couldn't understand the date/time. Try using 'Remind me to call at 11:30 PM'."})

    # Format reminder data
    reminder_data = {
        "task": task_message,
        "time": extracted_datetime.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save the reminder
    reminders = load_reminders()
    reminders.append(reminder_data)
    save_reminders(reminders)

    return jsonify({"response": f"Reminder added for {reminder_data['time']}!"})

@app.route("/list_reminders", methods=["GET"])
def list_reminders():
    """ List all saved reminders """
    reminders = load_reminders()
    return jsonify({"reminders": reminders})

@app.route("/delete_reminder", methods=["POST"])
def delete_reminder():
    """ Delete a reminder by task name """
    reminder_to_delete = request.json.get("message", "").strip()
    reminders = load_reminders()

    for reminder in reminders:
        if reminder["task"] in reminder_to_delete:
            reminders.remove(reminder)
            save_reminders(reminders)
            return jsonify({"response": "Reminder deleted!"})

    return jsonify({"response": "Reminder not found!"})

def check_reminders():
    """ Background process to check reminders and send notifications in real-time """
    while True:
        reminders = load_reminders()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for reminder in reminders[:]:  # Iterate over a copy to avoid modification issues
            reminder_time = datetime.strptime(reminder["time"], "%Y-%m-%d %H:%M:%S")

            # Ensure reminder fires exactly at the right second
            if reminder_time <= datetime.now():
                print(f"📢 Triggering Reminder: {reminder['task']} at {reminder['time']}")
                socketio.emit("reminder_notification", {"message": f"🔔 Reminder: {reminder['task']}"})

                # Remove reminder after triggering
                reminders.remove(reminder)
                save_reminders(reminders)

        time.sleep(1)  # Check every second

# Start background thread for reminder notifications
threading.Thread(target=check_reminders, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, debug=True)
