import requests
import gspread
import random
import json
import os

# --- CONFIGURATION ---
# PASTE YOUR FACEBOOK PAGE ID AND PAGE ACCESS TOKEN HERE
PAGE_ID = "717719538097140"
PAGE_ACCESS_TOKEN = "EAAOrNnT1OWABPFw4ZBQjXcqhQqnEI4EYhNeAIpUc8aTgZBAsHpRF7IXrPv6OSKw4JH15Nf0Oxf6dnqs2ye8SmUn7d3xMMb4K5pT0iVu1cJ98N0LrbdnqPT1RsRTX7ovFZBrWwBnlARbZCjzq7KvHDOESfZA887d5n5HchpFNUQ9Rby2MtnEpJpeTynaJLlw3YQ5vAxEwgjFSw9OAKPTfUAAxgnWcoOg7zAMcbDfMf0loZD"

# The name of your Google Sheet file
GOOGLE_SHEET_NAME = "english vocab" # Make sure to name your sheet this, or change this value

# This is the JSON credential you provided earlier.
GOOGLE_SHEETS_CREDENTIALS_JSON = '''
{
  "type": "service_account",
  "project_id": "telegram-english-bot-469411",
  "private_key_id": "469fb5a0700f36805ec8fb1db5ac3d0cae2bfb54",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCkt0LpwF6920R2\nnBMe1Z0CxXPqVXMt/cuitnjrysft6zJuPxB+c3fQ2c0EJXGWolO8P+ZxOB2LUckp\nInUnpi16+R8jKES2eZv0LTS9ZGx58CE8166AfXjKWLENat2AcAD2LF0u6qP6eI6w\n4snxuUkg+br/7ftE0W9GpnvHj2uRA51fpy10D4P3jpL2eXvqE2I0lnpPYEXt2sdL\nd3onuK+wCHiQV2jxQ37smOUqDnmyF04efV9WYbIMPNfUQ9M/38+O4EZovfQ6nARU\nstTUnZtPD04iaU/zZ9h4F8gSZiDdo7jzn9ImfjNatEKhkQmf0FD6YQajMM1ynjU/\nAuXGynQL6zRHCHAgMBAAECggEAM3ljy0nHMbyyldEjmfCE+ohsdL3ViGQgC5W9pT\ndyt+r2nGET5fhuspFF7OxIpYLf+R3dBXe8X9v0qcpR306jEoK7YE5i+7QCkwQRbl\n63tZohKnuASH4tf8qcte02AFvAKS4vBqjkCrOfH+8YZMeI9R3GGDGG7j5ddI0L2a\nF/oDrLqenf1ka1ilDSBN6B4yjUiKlbzgs8sE/kEM+ep7GujTvEfGfma1o852cghb\nN/s0yV7fznm1THgso8wqAXcvEs37GVgOU9T5Ob7aUiY0B3KNyavYLQP2J1tiOmfU\nglxOQyDB7pnMuCIDGD9GiwY7cmpU6ImrFeFkqYgopzSJuVKC5EnfQKBgQDXcoBBA\nEC5pygrJP/Gn4mdumxHFhy6cg0u8Fg1rUWdGjWJvupx5KUxHl8B/FrfNzUwOY1H0\nBomDanOWxFGnnnAhwuLu5DCyoY+T8C5qnmlAhtLS/MXkqOwlEpf1i6MO0kUAQ9Tm\nfTusiYTHh5VQon9v9n3CEHeyBww+udKnVfZAOPswKBgQDDuDohaCMH/fa+0oy9o5\nlxMPbDW+iByLp0nf2L4glun9c+i59RIRGbOnI6DiJPN7cdlXtQ7sxfaBje7mQ2S8\nP5hnZmRk0iVxG3sneqOH5kr6H4hOkvLSv5lDPInvixKT4mu7TC/eOjDUZtwPqXU6\niBWuopvK/L4gxTmEnnGahun+R3QKBgG0LJOLBUAEnG2uK1HJDEPqoPbxuCSdqRK\nCzwKL6lnzc/l9yYdPpnFRR/OAya4Pim2cHGfyo1TNBYxpweTP26OYNj3I9yHAA2X\nyU6clI2BiypG3pRffPjn4XL/WFoBWVxAz95FX57EALpr2yVsPsZlDSvx/D2fEfJB\nzV60eEv66WFAoGBALbknnx28rI+5WSy0oGROTwMhWFbyufEd3G8k4x2K44+u+ts\nmfI8TrGaCkgKETGpxOpWVn6gnnr/BDQy2BNtgLcAtUNL9+vKOHrZkAeXRzVbkqYj\nvawiMCfHwCRHueoDulqDqcnVVb7VcoGXLoeBrgtluVceu1TBXCmHLu5U4bqOm/ZA\noGBAKzBfNn9b3GY0ADPH+kTn9msOXdu9YLBsULF5D9RzpkOK9etTA68iv7yLLk\ntqVstT9eJQlFGFNlDODTbQKyb9nkBe7lGuk4i5u9q9CdPCQTA2l3KQQiQoZkXbTk\nuhKQwzxhqOFC1MsN2BSUY/SJsJHnaVaAqK9rRyUrPQ1TtHgv4rxzn\n-----END PRIVATE KEY-----
",
  "client_email": "google-sheets-reader@telegram-english-bot-469411.iam.gserviceaccount.com",
  "client_id": "113789285992319834928",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/google-sheets-reader%40telegram-english-bot-469411.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
'''

# File to store the index of the last word posted
PROGRESS_FILE = "progress.txt"

def get_google_sheet_data():
    """Connects to Google Sheets and fetches the vocabulary data."""
    try:
        # The gspread library uses the JSON string directly
        credentials = json.loads(GOOGLE_SHEETS_CREDENTIALS_JSON)
        gc = gspread.service_account_from_dict(credentials)
        
        # Open the sheet by its name
        worksheet = gc.open(GOOGLE_SHEET_NAME).sheet1
        
        # Get all records from the sheet (assumes first row is header)
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
    if PAGE_ID == "YOUR_PAGE_ID" or PAGE_ACCESS_TOKEN == "YOUR_PAGE_ACCESS_TOKEN":
        print("ERROR: Please update PAGE_ID and PAGE_ACCESS_TOKEN in the script.")
        return

    url = f"https://graph.facebook.com/v20.0/{PAGE_ID}/feed"
    params = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
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
        # Get wrong options from other words
        while len(options) < 4:
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
        while len(options) < 4:
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
        while len(options) < 4:
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
    
    all_data = get_google_sheet_data()
    if not all_data:
        print("Could not fetch data. Exiting.")
        return

    current_index = get_progress()

    if current_index >= len(all_data):
        print("All words have been posted. Resetting progress.")
        save_progress(0)
        current_index = 0
        post_to_facebook_page("We have completed our vocabulary list! The cycle will now start over. Keep learning!")
        return

    word_to_post = all_data[current_index]
    
    # Generate the question message
    message = generate_question(word_to_post, all_data)
    
    print(f"Generated Post:\n---\n{message}\n---")
    
    # Post to Facebook
    result = post_to_facebook_page(message)
    
    # If posting was successful, update the progress
    if result:
        save_progress(current_index + 1)
        print(f"Successfully posted word #{current_index + 1}: {word_to_post.get('Word')}")

if __name__ == "__main__":
    main()
