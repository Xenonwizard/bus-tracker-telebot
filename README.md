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
CREDENTIALS_JSON={"type": "service_account", "project_id": "...", "private_key": "..."}
```

> 💡 If `CREDENTIALS_JSON` is too large or multi-line, export it directly in terminal:
```bash
export CREDENTIALS_JSON="$(cat credentials.json)"
```

---

## 🧪 Run Locally

Start the bot server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

Expose it with [ngrok](https://ngrok.com/):

```bash
ngrok http 8080
```

Then set `WEBHOOK_URL=https://your-ngrok-url` in `.env`.

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

Then deploy with:

```bash
gcloud run deploy bus-tracker-bot \
  --image gcr.io/YOUR_PROJECT_ID/YOUR_IMAGE_NAME \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-secrets CREDENTIALS_JSON=credentials-json:latest \
  --set-env-vars TELE_TOKEN=your_bot_token,WEBHOOK_URL=https://your-service-url
```

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

---
