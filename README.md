# Facebook English Vocabulary Bot

## 1. Project Overview

This project is a fully automated bot that posts educational English vocabulary content to a Facebook page. It is powered by a Python script and runs automatically on schedule using GitHub Actions. The content is pulled directly from a private Google Sheet.

Its primary goal is to provide engaging, daily content in the form of new words and interactive quizzes to help users improve their vocabulary.

---

## 2. Features

The bot has four distinct, automated functions:

1.  **Daily Vocabulary Words**
    *   **What it does:** Posts a set of 3 new vocabulary words with their meanings, synonyms, antonyms, and an example sentence.
    *   **Schedule:** Every day at 7:00 AM IST.

2.  **Daily MCQ Quiz**
    *   **What it does:** Generates and posts a 9-question multiple-choice quiz based on the 3 words from that morning's post.
    *   **Schedule:** Every day at 4:00 PM IST.

3.  **Daily MCQ Answers**
    *   **What it does:** Posts the correct answers to the quiz from earlier in the day.
    *   **Schedule:** Every day at 9:00 PM IST.

4.  **Weekly Summary**
    *   **What it does:** Posts a formatted summary of the last 21 words that have been taught.
    *   **Schedule:** Every Sunday at 9:00 AM IST.

---

## 3. How It Works

The bot operates through the interaction of a Python script and a GitHub Actions workflow.

### Core Components

*   **`main.py`**: The main Python script that contains all the logic for fetching data, formatting posts, and sending them to Facebook.
*   **`.github/workflows/main.yml`**: The GitHub Actions workflow file. This file defines the schedules and tells GitHub how to run the `main.py` script for each task.
*   **`requirements.txt`**: A list of the necessary Python libraries that the script depends on (e.g., for accessing Google Sheets and making web requests).
*   **`progress.json`**: This file acts as the bot's long-term memory for the daily words. It stores the index of the next word to be posted, ensuring the bot doesn't repeat itself and posts words in sequence.
*   **`quiz_state.json`**: This file is a short-term memory file. It stores the questions and correct answers for the quiz that was posted at 4 PM. The bot reads this file at 9 PM to post the correct answers, then clears the file.

### Automation Flow

1.  At a scheduled time (e.g., 7:00 AM IST), GitHub Actions triggers the workflow.
2.  The workflow determines which task to run based on the schedule (e.g., `daily_words`).
3.  It sets up a virtual machine, installs the Python libraries from `requirements.txt`, and runs the `main.py` script.
4.  The Python script checks the `TASK` variable, executes the corresponding function (e.g., `send_daily_words()`), and posts to Facebook.
5.  After the script runs, the workflow commits any changes to `progress.json` or `quiz_state.json` back to the repository to save its state.

---

## 4. Configuration & Management

### Google Sheet Setup

*   The bot reads from a Google Sheet named **"english vocab"**.
*   The sheet **must** have the following columns: `Word`, `Meaning`, `Synonyms`, `Antonyms`, `Example Sentence`.
*   The Google Sheet must be shared with the `client_email` found in your Google credentials JSON file, giving it at least "Viewer" access.

### GitHub Secrets

All private credentials are stored as GitHub Secrets. To configure the bot, you need to set the following secrets in your repository's `Settings` > `Secrets and variables` > `Actions`:

*   `PAGE_ID`: The ID of your Facebook Page.
*   `PAGE_ACCESS_TOKEN`: A Page Access Token with permissions to post content.
*   `GOOGLE_SHEETS_CREDENTIALS_JSON`: The JSON credentials for your Google service account, pasted as a single line of text.

### Manual Control

You can run any task manually from the GitHub **Actions** tab:
1.  Select the "Post to Facebook Page" workflow.
2.  Click the "Run workflow" button.
3.  Use the dropdown menu to choose which task you want to run (`daily_words`, `mcq_questions`, etc.).

### Resetting Progress

To make the bot start over from the very first word:
1.  Open the `progress.json` file.
2.  Change its content to: `{"daily_index": 0}`
3.  Save and push this change to the GitHub repository.

The next time the `daily_words` task runs, it will start from word #1.

---

This project is now complete and fully operational. We hope it works well for you!
