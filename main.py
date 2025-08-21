import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import random

# --- Configuration ---
GOOGLE_SHEETS_CREDENTIALS_JSON = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_JSON")
PAGE_ID = os.environ.get("PAGE_ID")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
GOOGLE_SHEET_NAME = "english vocab"
PROGRESS_FILE = "progress.json"
QUIZ_STATE_FILE = "quiz_state.json"

# --- Utility Functions ---
def to_bold(text):
    """Converts a string to bold Unicode characters."""
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
    res = ""
    for char in text:
        idx = normal.find(char)
        if idx != -1:
            res += bold[idx]
        else:
            res += char
    return res

def get_ist_timestamp():
    """Returns the current date and time in IST, formatted for the post."""
    utc_now = datetime.now(ZoneInfo("UTC"))
    ist_now = utc_now.astimezone(ZoneInfo("Asia/Kolkata"))
    date_str = ist_now.strftime("%d/%m/%Y")
    time_str = ist_now.strftime("%H:%M:%S")
    return f"Date: {date_str}\nTime: {time_str} (IST)"

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

def get_quiz_state():
    """Reads the current quiz state from a file."""
    if os.path.exists(QUIZ_STATE_FILE):
        with open(QUIZ_STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_quiz_state(state):
    """Saves the current quiz state to a file."""
    with open(QUIZ_STATE_FILE, "w") as f:
        json.dump(state, f)

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
    for i, word_data in enumerate(words_to_send):
        word_number = daily_index + i + 1
        part = (
            f"{to_bold(str(word_number) + '. Word:')} {word_data.get('Word', '')}\n"
            f"{to_bold('Meaning:')} {word_data.get('Meaning', '')}\n"
            f"{to_bold('Synonyms:')} {word_data.get('Synonyms', '')}\n"
            f"{to_bold('Antonyms:')} {word_data.get('Antonyms', '')}\n"
            f"{to_bold('Example:')} {word_data.get('Example Sentence', '')}"
        )
        message_parts.append(part)

    timestamp = get_ist_timestamp()
    full_message = f"{timestamp}\n\n---\n\n" + "\n\n---\n\n".join(message_parts)
    
    if post_to_facebook_page(full_message):
        progress["daily_index"] = daily_index + len(words_to_send)
        save_progress(progress)
        print(f"Successfully sent {len(words_to_send)} words. Next index: {progress['daily_index']}")

def send_weekly_summary(all_data):
    """Sends a summary of the last 21 words to Facebook in the full format."""
    print("Attempting to send weekly summary...")
    progress = get_progress()
    current_index = progress.get("daily_index", 0)

    start_index = max(0, current_index - 21)
    words_for_summary = all_data[start_index:current_index]

    if not words_for_summary:
        print("Not enough words posted yet for a weekly summary.")
        return

    summary_header = f"--- Weekly Vocabulary Summary: Words {start_index + 1} to {current_index} ---"
    message_parts = [to_bold(summary_header)]

    for i, word_data in enumerate(words_for_summary):
        word_number = start_index + i + 1
        part = (
            f"{to_bold(str(word_number) + '. Word:')} {word_data.get('Word', '')}\n"
            f"{to_bold('Meaning:')} {word_data.get('Meaning', '')}\n"
            f"{to_bold('Synonyms:')} {word_data.get('Synonyms', '')}\n"
            f"{to_bold('Antonyms:')} {word_data.get('Antonyms', '')}\n"
            f"{to_bold('Example:')} {word_data.get('Example Sentence', '')}"
        )
        message_parts.append(part)

    timestamp = get_ist_timestamp()
    full_message = f"{timestamp}\n\n---\n\n" + "\n\n---\n\n".join(message_parts)
    post_to_facebook_page(full_message)


def generate_and_post_mcqs(all_data):
    """Generates and posts 9 MCQs based on the day's 3 words."""
    print("Attempting to generate and post MCQs...")
    progress = get_progress()
    # The index points to the *next* set of words, so we subtract 3 to get the current set.
    daily_index = progress.get("daily_index", 0) - 3
    if daily_index < 0:
        print("Not enough words have been posted to generate a quiz.")
        return

    words_for_quiz = all_data[daily_index : daily_index + 3]
    
    # Create a pool of potential wrong answers
    distractor_pool = {
        "Meaning": [d.get("Meaning") for d in all_data if d.get("Meaning")],
        "Synonyms": [d.get("Synonyms") for d in all_data if d.get("Synonyms")],
        "Antonyms": [d.get("Antonyms") for d in all_data if d.get("Antonyms")]
    }

    quiz_questions = []
    question_number = 1
    
    for word_data in words_for_quiz:
        word = word_data.get("Word")
        # Question types: Meaning, Synonyms, Antonyms
        for q_type in ["Meaning", "Synonyms", "Antonyms"]:
            correct_answer = word_data.get(q_type)
            if not correct_answer: continue

            # Get 2 wrong answers
            distractors = random.sample([
                ans for ans in distractor_pool[q_type] if ans != correct_answer
            ], 2)
            
            options = distractors + [correct_answer]
            random.shuffle(options)
            
            quiz_questions.append({
                "question_text": to_bold(f"Q{question_number}: What is/are the {q_type.lower()} of \"{word}\"?"),
                "options": options,
                "correct_answer_text": correct_answer
            })
            question_number += 1

    if not quiz_questions:
        print("Could not generate any quiz questions.")
        return

    # Format for Facebook post
    post_parts = [to_bold("Here is your quiz!")]
    for q in quiz_questions:
        options_str = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(q["options"])])
        post_parts.append(f"{q['question_text']}\n{options_str}")
    
    timestamp = get_ist_timestamp()
    full_message = f"{timestamp}\n\n" + "\n\n".join(post_parts)
    
    if post_to_facebook_page(full_message):
        save_quiz_state(quiz_questions)
        print("Successfully generated and posted quiz. State saved.")

def post_mcq_answers():
    """Posts the answers to the most recently generated quiz."""
    print("Attempting to post MCQ answers...")
    quiz_state = get_quiz_state()

    if not quiz_state:
        print("No quiz state found. Cannot post answers.")
        return

    post_parts = [to_bold("Here are the answers!")]
    for i, q in enumerate(quiz_state):
        post_parts.append(f"A{i+1}: {q['correct_answer_text']}")
        
    timestamp = get_ist_timestamp()
    full_message = f"{timestamp}\n\n" + "\n".join(post_parts)
    
    if post_to_facebook_page(full_message):
        # Clear the state after posting answers
        save_quiz_state([])
        print("Successfully posted answers and cleared quiz state.")



# --- Main Execution ---
if __name__ == "__main__":
    task = os.environ.get("TASK")
    
    sheet_data = get_google_sheet()

    if sheet_data:
        if task == "daily_words":
            send_daily_words(sheet_data)
        elif task == "weekly_summary":
            send_weekly_summary(sheet_data)
        elif task == "mcq_questions":
            generate_and_post_mcqs(sheet_data)
        elif task == "mcq_answers":
            post_mcq_answers()
        else:
            print("No valid TASK environment variable set. Exiting.")