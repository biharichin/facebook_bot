import requests
import gspread
import random
import json
import os
import base64

# --- CONFIGURATION ---
# The script will get these values from your GitHub Secrets
PAGE_ID = os.getenv("PAGE_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")

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
        return f"What is the meaning of '{word}'?\n\n{options_str}\n\n#Vocabulary #EnglishQuiz"

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
        return f"What are the synonyms of '{word}'?\n\n{options_str}\n\n#Vocabulary #Synonyms"

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
        return f"What are the antonyms of '{word}'?\n\n{options_str}\n\n#Vocabulary #Antonyms"

    elif question_type == "unscramble":
        scrambled_word = "".join(random.sample(word, len(word)))
        return f"Unscramble the letters to find the correct word:\n\n{scrambled_word}\n\n#Vocabulary #Unscramble"

    return f"Let's learn a new word: {word}\nMeaning: {word_data.get('Meaning', '')}"

def main():
    """Main function to run the bot."""
    print("Bot starting...")
    print("Running in test mode...")
    post_to_facebook_page("Hello from my bot! This is a test.")
    print("Test finished.")

if __name__ == "__main__":
    main()
