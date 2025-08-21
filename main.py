import requests
import gspread
import random
import json
import os
import base64
from datetime import datetime

# --- CONFIGURATION ---
# The script will get these values from your GitHub Secrets
PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")

# The name of your Google Sheet file
GOOGLE_SHEET_NAME = "english vocab"

# File to store the index of the last word posted for daily words
DAILY_PROGRESS_FILE = "daily_progress.txt"
# File to store the index of the last word for weekly summary
WEEKLY_PROGRESS_FILE = "weekly_progress.txt"


def get_google_sheet_data():
    """Connects to Google Sheets and fetches the vocabulary data."""
    try:
        # Decode the base64 secret, then decode the bytes to a string, then parse the JSON
        decoded_creds = base64.b64decode(GOOGLE_SHEETS_CREDENTIALS_JSON)
        decoded_creds_text = decoded_creds.decode('utf-8')
        credentials = json.loads(decoded_creds_text)
        
        gc = gspread.service_account_from_dict(credentials)
        worksheet = gc.open(GOOGLE_SHEET_NAME).sheet1
        data = worksheet.get_all_records()
        print("Successfully fetched data from Google Sheet.")
        return data
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        return None

def get_progress(progress_file):
    """Reads the index from the specified progress file."""
    if not os.path.exists(progress_file):
        return 0
    with open(progress_file, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_progress(progress_file, index):
    """Saves the next index to the specified progress file."""
    with open(progress_file, "w") as f:
        f.write(str(index))

def post_to_facebook_page(message):
    """Posts a message to the configured Facebook Page."""
    if not PAGE_ID or not PAGE_ACCESS_TOKEN:
        print("ERROR: PAGE_ID or PAGE_ACCESS_TOKEN is missing.")
        return None

    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
    params = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        print("Successfully posted to Facebook page.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Facebook: {e}")
        print(f"Response body: {e.response.text if e.response else 'No response'}")
        return None

def send_daily_words_to_facebook(all_data):
    """Sends 3 daily vocabulary words to Facebook."""
    print("Attempting to send daily words to Facebook...")
    current_start_index = get_progress(DAILY_PROGRESS_FILE) # Use a clearer name

    words_to_send = []
    # Calculate the actual words to send, handling wrap-around
    for i in range(3):
        index_to_fetch = (current_start_index + i) % len(all_data) # Use modulo for continuous cycling
        words_to_send.append(all_data[index_to_fetch])

    if not words_to_send:
        print("No words to send to Facebook for daily post.")
        return

    facebook_message_parts = []
    for word_data in words_to_send:
        word = word_data.get("Word", "").strip()
        meaning = word_data.get("Meaning", "").strip()
        synonyms = word_data.get("Synonyms", "").strip()
        antonyms = word_data.get("Antonyms", "").strip()
        example = word_data.get("Example Sentence", "").strip()

        part = (
            f"Word: {word}\n"
            f"Meaning: {meaning}\n"
            f"Synonyms: {synonyms}\n"
            f"Antonyms: {antonyms}\n"
            f"Example: {example}\n"
        )
        facebook_message_parts.append(part)

    full_facebook_message = "\n---\n".join(facebook_message_parts)

    result = post_to_facebook_page(full_facebook_message)
    if result:
        # Calculate the next starting index
        next_start_index = (current_start_index + len(words_to_send)) % len(all_data)
        save_progress(DAILY_PROGRESS_FILE, next_start_index)
        print(f"Successfully sent {len(words_to_send)} words to Facebook. Next daily index: {next_start_index}")
    else:
        print("Failed to send daily words to Facebook.")

def send_weekly_summary_to_facebook(all_data):
    """Sends a weekly summary of learned words to Facebook."""
    print("Attempting to send weekly summary to Facebook...")
    weekly_current_index = get_progress(WEEKLY_PROGRESS_FILE)

    # Calculate the start index for the last 21 words
    # Handle cases where there aren't 21 words yet
    start_index = max(0, weekly_current_index - 21)
    
    words_for_summary = all_data[start_index:weekly_current_index]

    if not words_for_summary:
        print("No words to summarize for the week.")
        return

    summary_message_parts = ["Weekly Vocabulary Summary:\n"]
    for i, word_data in enumerate(words_for_summary):
        word = word_data.get("Word", "").strip()
        meaning = word_data.get("Meaning", "").strip()
        summary_message_parts.append(f"{i+1}. {word}: {meaning}")

    full_summary_message = "\n".join(summary_message_parts)

    result = post_to_facebook_page(full_summary_message)
    if result:
        save_progress(WEEKLY_PROGRESS_FILE, weekly_current_index) # Progress is not incremented for summary, just marks it as sent
        print(f"Successfully sent weekly summary to Facebook. Summarized {len(words_for_summary)} words.")
    else:
        print("Failed to send weekly summary to Facebook.")

def main():
    """Main function to run the bot."""
    print("Bot starting...")
    all_data = get_google_sheet_data()
    if not all_data:
        print("Could not fetch data. Exiting.")
        return

    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    current_weekday = now.weekday() # Monday is 0, Sunday is 6

    # Check if it's 7:00 AM IST for daily words
    if True: # TEMPORARY: For testing daily words
        print("It's 7:00 AM IST. Sending daily words to Facebook.")
        send_daily_words_to_facebook(all_data)
    else:
        print(f"Current time is {current_hour:02d}:{current_minute:02d}. Not 7:00 AM IST for daily words.")

    # Check if it's Sunday (weekday 6) and 9:00 AM IST for weekly summary
    if True: # TEMPORARY: For testing weekly summary
        print("It's Sunday 9:00 AM IST. Sending weekly summary to Facebook.")
        send_weekly_summary_to_facebook(all_data)
    else:
        print(f"Current time is {current_hour:02d}:{current_minute:02d} on weekday {current_weekday}. Not Sunday 9:00 AM IST for weekly summary.")

    print("Bot finished daily check.")

if __name__ == "__main__":
    main()
