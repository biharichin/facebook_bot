
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
import datetime

# --- Configuration ---
GOOGLE_SHEETS_CREDENTIALS_JSON = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
PAGE_ID = os.environ.get("PAGE_ID")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GOOGLE_SHEET_NAME = "english vocab"
PROGRESS_FILE = "progress.json"

# --- Google Sheets Setup ---
def get_google_sheet():
    """Connects to Google Sheets and returns the worksheet."""
    try:
        creds_json = json.loads(GOOGLE_SHEETS_CREDENTIALS_JSON)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        return sheet.get_all_records()
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None

# --- Progress Tracking ---
def get_progress():
    """Reads the current progress (index) from a file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"daily_index": 0}

def save_progress(progress):
    """Saves the current progress (index) to a file."""
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

# --- Facebook Posting ---
def post_to_facebook_page(message):
    """Posts a message to the Facebook page."""
    url = f"https://graph.facebook.com/v18.0/{PAGE_ID}/feed"
    params = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        print("Successfully posted to Facebook page.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Facebook: {e}")
        print(f"Response: {response.text}")
        return False

# --- Bot Features ---
def send_daily_words(all_data):
    """Sends 3 daily vocabulary words to Facebook."""
    print("Attempting to send daily words...")
    progress = get_progress()
    daily_index = progress.get("daily_index", 0)

    words_to_send = all_data[daily_index : daily_index + 3]

    if not words_to_send:
        print("No more words to send. Resetting for next cycle.")
        daily_index = 0
        words_to_send = all_data[daily_index : daily_index + 3]


    message_parts = []
    for word_data in words_to_send:
        part = (
            f"Word: {word_data.get('Word', '')}\n"
            f"Meaning: {word_data.get('Meaning', '')}\n"
            f"Synonyms: {word_data.get('Synonyms', '')}\n"
            f"Antonyms: {word_data.get('Antonyms', '')}\n"
            f"Example: {word_data.get('Example Sentence', '')}"
        )
        message_parts.append(part)

    full_message = "\n\n---\n\n".join(message_parts)
    
    if post_to_facebook_page(full_message):
        progress["daily_index"] = daily_index + len(words_to_send)
        save_progress(progress)
        print(f"Successfully sent {len(words_to_send)} words. Next index: {progress['daily_index']}")

def send_weekly_summary(all_data):
    """Sends a summary of the last 21 words to Facebook."""
    print("Attempting to send weekly summary...")
    progress = get_progress()
    current_index = progress.get("daily_index", 0)
    
    # Get the last 21 words, or fewer if not enough have been posted
    start_index = max(0, current_index - 21)
    words_for_summary = all_data[start_index:current_index]

    if not words_for_summary:
        print("Not enough words posted yet for a weekly summary.")
        return

    summary_header = f"Weekly Vocabulary Summary: Words {start_index + 1} to {current_index}"
    word_list = [f"- {word_data.get('Word', '')}" for word_data in words_for_summary]
    
    full_message = f"{summary_header}\n\n" + "\n".join(word_list)
    
    post_to_facebook_page(full_message)

# --- Main Execution ---
if __name__ == "__main__":
    # This script will be triggered by GitHub Actions based on the day.
    # We use an environment variable in the workflow to decide which function to run.
    task = os.environ.get("TASK")
    
    sheet_data = get_google_sheet()

    if sheet_data:
        if task == "daily_words":
            send_daily_words(sheet_data)
        elif task == "weekly_summary":
            send_weekly_summary(sheet_data)
        else:
            print("No valid TASK environment variable set. Exiting.")
