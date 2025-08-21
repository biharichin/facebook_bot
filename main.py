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
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The name of your Google Sheet file
GOOGLE_SHEET_NAME = "english vocab"

# File to store the index of the last word posted
PROGRESS_FILE = "progress.txt"
TELEGRAM_PROGRESS_FILE = "telegram_progress.txt" # New progress file for Telegram

def send_telegram_message(chat_id, message):
    """Sends a message to a specified Telegram chat."""
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN or chat_id is missing for Telegram.")
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML" # Use HTML for formatting
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        print(f"Successfully sent message to Telegram chat {chat_id}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")
        print(f"Response body: {e.response.text if e.response else 'No response'}")
        return None

# The name of your Google Sheet file
GOOGLE_SHEET_NAME = "english vocab"

# File to store the index of the last word posted
PROGRESS_FILE = "progress.txt"

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

def get_progress():
    """Reads the index from the progress file."""
    if not os.path.exists(PROGRESS_FILE):
        return 0
    with open(PROGRESS_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_progress(index):
    """Saves the next index to the progress file."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(index))

def get_telegram_progress():
    """Reads the index from the Telegram progress file."""
    if not os.path.exists(TELEGRAM_PROGRESS_FILE):
        return 0
    with open(TELEGRAM_PROGRESS_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_telegram_progress(index):
    """Saves the next index to the Telegram progress file."""
    with open(TELEGRAM_PROGRESS_FILE, "w") as f:
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

def generate_question(word_data, all_data):
    """Generates a random question string from the word data."""
    question_type = random.choice(["meaning_mcq", "synonym_mcq", "antonym_mcq", "unscramble"])
    word = word_data.get("Word", "").strip()

    # Get current date and time
    now = datetime.now()
    current_datetime_str = now.strftime("%Y-%m-%d %H:%M:%S IST") # Format as YYYY-MM-DD HH:MM:SS IST

    common_suffix = "\n\n#ielts #govt_exam #group_d_exam\n\nAnswer would be published evening 5:00 PM IST."
    
    if question_type == "meaning_mcq":
        correct_answer = word_data.get("Meaning", "").strip()
        options = {correct_answer}
        while len(options) < 4 and len(options) < len(all_data):
            random_word = random.choice(all_data)
            wrong_option = random_word.get("Meaning", "").strip()
            if wrong_option and wrong_option != correct_answer:
                options.add(wrong_option)
        
        shuffled_options = random.sample(list(options), len(options))
        options_str = "\n".join([f"  {chr(65+i)}) {opt}" for i, opt in enumerate(shuffled_options)])
        return f"Date & Time: {current_datetime_str}\n\nWhat is the meaning of '{word}'?\n\n{options_str}\n\n#Vocabulary #EnglishQuiz{common_suffix}"

    elif question_type == "synonym_mcq":
        correct_answer = word_data.get("Synonyms", "").strip()
        options = {correct_answer}
        while len(options) < 4 and len(options) < len(all_data):
            random_word = random.choice(all_data)
            wrong_option = random_word.get("Synonyms", "").strip()
            if wrong_option and wrong_option != correct_answer:
                options.add(wrong_option)

        shuffled_options = random.sample(list(options), len(options))
        options_str = "\n".join([f"  {chr(65+i)}) {opt}" for i, opt in enumerate(shuffled_options)])
        return f"Date & Time: {current_datetime_str}\n\nWhat are the synonyms of '{word}'?\n\n{options_str}\n\n#Vocabulary #Synonyms{common_suffix}"

    elif question_type == "antonym_mcq":
        correct_answer = word_data.get("Antonyms", "").strip()
        options = {correct_answer}
        while len(options) < 4 and len(options) < len(all_data):
            random_word = random.choice(all_data)
            wrong_option = random_word.get("Antonyms", "").strip()
            if wrong_option and wrong_option != correct_answer:
                options.add(wrong_option)

        shuffled_options = random.sample(list(options), len(options))
        options_str = "\n".join([f"  {chr(65+i)}) {opt}" for i, opt in enumerate(shuffled_options)])
        return f"Date & Time: {current_datetime_str}\n\nWhat are the antonyms of '{word}'?\n\n{options_str}\n\n#Vocabulary #Antonyms{common_suffix}"

    elif question_type == "unscramble":
        scrambled_word = "".join(random.sample(word, len(word)))
        return f"Date & Time: {current_datetime_str}\n\nUnscramble the letters to find the correct word:\n\n{scrambled_word}\n\n#Vocabulary #Unscramble{common_suffix}"

    return f"Date & Time: {current_datetime_str}\n\nLet's learn a new word: {word}\nMeaning: {word_data.get('Meaning', '')}{common_suffix}"

def send_daily_words_to_telegram(all_data):
    """Sends 3 daily vocabulary words to Telegram."""
    print("Attempting to send daily words to Telegram...")
    telegram_current_index = get_telegram_progress()
    
    words_to_send = []
    for i in range(3):
        if telegram_current_index + i < len(all_data):
            words_to_send.append(all_data[telegram_current_index + i])
        else:
            # If we run out of words, reset for the next cycle
            print("Reached end of vocabulary list for Telegram. Resetting progress.")
            telegram_current_index = 0
            save_telegram_progress(0)
            words_to_send.append(all_data[telegram_current_index + i]) # Add from the beginning

    if not words_to_send:
        print("No words to send to Telegram.")
        return

    telegram_message_parts = []
    for word_data in words_to_send:
        word = word_data.get("Word", "").strip()
        meaning = word_data.get("Meaning", "").strip()
        synonyms = word_data.get("Synonyms", "").strip()
        antonyms = word_data.get("Antonyms", "").strip()
        example = word_data.get("Example Sentence", "").strip()

        part = (
            f"<b>Word:</b> {word}\n"
            f"<b>Meaning:</b> {meaning}\n"
            f"<b>Synonyms:</b> {synonyms}\n"
            f"<b>Antonyms:</b> {antonyms}\n"
            f"<b>Example:</b> {example}\n"
        )
        telegram_message_parts.append(part)

    full_telegram_message = "\n---\n".join(telegram_message_parts)

    result = send_telegram_message(TELEGRAM_CHAT_ID, full_telegram_message)
    if result:
        save_telegram_progress(telegram_current_index + len(words_to_send))
        print(f"Successfully sent {len(words_to_send)} words to Telegram. Next index: {telegram_current_index + len(words_to_send)}")
    else:
        print("Failed to send daily words to Telegram.")

def send_weekly_summary_to_telegram(all_data):
    """Sends a weekly summary of learned words to Telegram."""
    print("Attempting to send weekly summary to Telegram...")
    telegram_current_index = get_telegram_progress()

    # Calculate the start index for the last 21 words
    # Handle cases where there aren't 21 words yet
    start_index = max(0, telegram_current_index - 21)
    
    words_for_summary = all_data[start_index:telegram_current_index]

    if not words_for_summary:
        print("No words to summarize for the week.")
        return

    summary_message_parts = ["<b>Weekly Vocabulary Summary:</b>\n"]
    for i, word_data in enumerate(words_for_summary):
        word = word_data.get("Word", "").strip()
        meaning = word_data.get("Meaning", "").strip()
        summary_message_parts.append(f"{i+1}. <b>{word}:</b> {meaning}")

    full_summary_message = "\n".join(summary_message_parts)

    result = send_telegram_message(TELEGRAM_CHAT_ID, full_summary_message)
    if result:
        print(f"Successfully sent weekly summary to Telegram. Summarized {len(words_for_summary)} words.")
    else:
        print("Failed to send weekly summary to Telegram.")

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
    if current_hour == 7 and current_minute == 0:
        print("It's 7:00 AM IST. Sending daily words to Telegram.")
        send_daily_words_to_telegram(all_data)
    else:
        print(f"Current time is {current_hour:02d}:{current_minute:02d}. Not 7:00 AM IST for daily words.")

    # Check if it's Sunday (weekday 6) and 9:00 AM IST for weekly summary
    if current_weekday == 6 and current_hour == 9 and current_minute == 0:
        print("It's Sunday 9:00 AM IST. Sending weekly summary to Telegram.")
        send_weekly_summary_to_telegram(all_data)
    else:
        print(f"Current time is {current_hour:02d}:{current_minute:02d} on weekday {current_weekday}. Not Sunday 9:00 AM IST for weekly summary.")

    # Existing Facebook posting logic
    current_index = get_progress()
    if current_index >= len(all_data):
        print("All words have been posted. Resetting progress.")
        save_progress(0)
        post_to_facebook_page("We have completed our vocabulary list! The cycle will now start over. Keep learning!")
        return

    word_to_post = all_data[current_index]
    message = generate_question(word_to_post, all_data)
    print(f"Generated Post:\n---\n{message}\n---")
    
    result = post_to_facebook_page(message)
    if result:
        save_progress(current_index + 1)
        print(f"Successfully posted word #{current_index + 1}: {word_to_post.get('Word')}")



if __name__ == "__main__":
    main()
