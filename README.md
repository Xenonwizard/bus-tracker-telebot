# 🚍 Bus Tracker Telegram Bot

A Telegram bot for tracking bus journey checkpoints, logging data into Google Sheets with support for live status updates, recovery, and webhook integration.

---

## 📦 Project Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in your project root:

```env
TELE_TOKEN=your_telegram_bot_token
WEBHOOK_URL=https://your-public-url.com
JSON_PATHNAME=<PATH TO JSON CREDENTIALS>
```

---

## 🧪 Run Locally

Start the bot server:

Expose it with [ngrok](https://ngrok.com/):

```bash
ngrok http 8080
```

Then set `WEBHOOK_URL=https://your-ngrok-url` in `.env`.

UNCOMMENT this code in bot.py (For Running Locally):

```bash
JSON_TOKEN = os.getenv('JSON_PATHNAME')
gc = gspread.service_account(filename=JSON_TOKEN)
```

COMMENT this code in bot.py (Cloud Run Code)

```bash
json_str = os.getenv("JSON_PATHNAME")  # or 'JSON_PATHNAME' if that’s what you're using

if not json_str:
    raise ValueError("Missing CREDENTIALS_JSON environment variable")

# Parse the JSON string into a Python dict
info = json.loads(json_str)

# Build credentials from the info
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

credentials = service_account.Credentials.from_service_account_info(info, scopes=scopes)

gc = gspread.authorize(credentials)
```
Run the code (Alternative is to run using docker):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```
---

## 🐳 Docker Usage

### Build the Docker Image

```bash
docker build -t bus-tracker-bot .
```

### Run the Docker Container

```bash
docker run --env-file .env -p 8080:8080 bus-tracker-bot
```

---

## ☁️ Deploy to Cloud Run

Use [Google Secret Manager](https://cloud.google.com/secret-manager) to store the contents of `credentials.json`.

Uncomment the cloud run code as mentioned above.

Build the Docker Image as mentioned above.

Deploy docker image on GCR:

```bash
gcloud builds submit --tag gcr.io/live-telebot-production/bus-tracker-bot
```

Then deploy with:

```bash
gcloud run deploy bus-tracker-bot \
  --image gcr.io/YOUR_PROJECT_ID/YOUR_IMAGE_NAME \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-secrets JSON_PATHNAME=credentials-json:latest \
  --set-env-vars TELE_TOKEN=your_bot_token,WEBHOOK_URL=https://your-service-url
```
Or I usually use the console itself, its much easier.

---

## 🗒️ Google Sheets Setup

- Share your Google Sheet with the service account email (found in `credentials.json`)
- The sheet must contain a tab called `D1` with the appropriate column headers.
- The bot reads/writes to it dynamically based on bus number, wave, checkpoints, and remarks.

---

## ✅ Features

- ✅ Telegram step-by-step bot input
- ✅ Live Google Sheet updates
- ✅ Lost session recovery
- ✅ Passenger mismatch remark tracking
- ✅ Cloud-compatible via webhook
- ✅ Local or containerized development
- ✅ Some Keynote reminders for BUS IC
- ✅ Re-edit your bus details

---
