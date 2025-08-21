# Project Plan: Facebook & Messenger Vocabulary Bot

## 1. Vision

To build an automated English vocabulary learning platform that starts as a free, community-focused tool on a Facebook Page and evolves into a monetized, subscription-based service delivered via Facebook Messenger.

## 2. Project Phases

This project is broken into two distinct phases. Phase 1 is designed to be completely free to operate, focusing on building an audience. Phase 2 introduces a server and database to handle payments and personalized user interactions.

---

### **Phase 1: Community Building (The Free Page Bot)**

**Objective:** To grow an engaged community and build brand presence by posting free, daily vocabulary questions to a public Facebook Page.

**Implementation Strategy (Zero-Cost Model):**

*   **Content Source:** A **Google Sheet** will store all vocabulary words, definitions, and multiple-choice options. This makes content management easy and free.
*   **Automation Engine:** **GitHub Actions** will be used to run a script on a daily schedule. This is the key to the zero-cost model, as it requires no paid server.
*   **Core Logic:** A **Python script** will read from the Google Sheet, randomly generate one of four question types (MCQ on meaning/synonyms/antonyms, or an unscramble puzzle), and post it to the Facebook Page.
*   **Facebook Integration:** The script will use the **Facebook Graph API** to publish posts, requiring a free Facebook Developer App and a Page Access Token.

**User Interaction in Phase 1:**
*   The bot posts a new question daily to the public Facebook Page timeline.
*   Users engage publicly by commenting or reacting.

---

### **Phase 2: Monetization (The Subscription Messenger Bot)**

**Objective:** To convert the audience from Phase 1 into paying subscribers by offering a premium, personalized learning experience through direct messages.

**Monetization Model:**
*   **21-Day Free Trial:** New users get 21 days of free questions sent directly to their Messenger.
*   **Subscription:** After the trial, users must pay a subscription fee to continue receiving daily questions.

**Implementation Strategy (Server-Based Model):**

This phase requires a backend server to manage individual users, track trials, and process payments.

*   **Platform:** The interaction moves from the public Facebook Page to private **Facebook Messenger**.
*   **Backend Server:** A lightweight Python web framework like **FastAPI** or **Flask**.
*   **Hosting:** A platform-as-a-service like **Render** or **Heroku**.
*   **Database:** A database (e.g., **PostgreSQL**) to store user data (Facebook ID, trial status, subscription status, etc.).
*   **Payment Gateway:** Integration with a service like **Stripe** to handle recurring subscription payments.

## 3. Transitioning from Phase 1 to Phase 2

Phase 1 seamlessly sets the stage for Phase 2:
*   **Audience is Ready:** You will have an established audience on your Facebook Page to market the premium Messenger service to.
*   **Content is Reusable:** The Google Sheet full of vocabulary can still be used as the content source for the Messenger bot.
*   **Code is Adaptable:** The core Python logic for generating questions can be lifted from the Phase 1 script and integrated into the Phase 2 backend.
