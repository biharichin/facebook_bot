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