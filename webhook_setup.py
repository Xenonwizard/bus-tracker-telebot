# webhook_setup.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELE_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={
    "url": f"{WEBHOOK_URL}/{BOT_TOKEN}"
})

print(r.status_code, r.text)
