# webhook_setup.py
import os
import requests
from dotenv import load_dotenv
import requests

load_dotenv()

BOT_TOKEN = os.getenv("TELE_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def set_webhook_once():
    try:
        BOT_TOKEN = os.getenv("TELE_TOKEN")
        WEBHOOK_URL = os.getenv("WEBHOOK_URL")
        full_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"

        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={"url": full_url})
        print(f"📡 Webhook setup status: {r.status_code} {r.text}")
    except Exception as e:
        print("❌ Failed to set webhook:", str(e))

set_webhook_once()