from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from bot import process_update_from_webhook
import uvicorn
import requests

load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("TELE_TOKEN")
print("📢 Loaded BOT_TOKEN:", BOT_TOKEN)


@app.get("/")
def root():
    return {"message": "Hello from Cloud Run!"}


@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    print("🚨 Incoming Telegram webhook hit!")
    try:
        body = await request.body()
        print("📦 Raw body:", body.decode("utf-8")[:100])
        process_update_from_webhook(body.decode("utf-8"))
        return {"ok": True}
    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        return {"error": str(e)}


def set_webhook_once():
    BOT_TOKEN = os.getenv("TELE_TOKEN")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    if not BOT_TOKEN or not WEBHOOK_URL:
        print("❌ TELE_TOKEN or WEBHOOK_URL not set")
        return

    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    try:
        res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={"url": webhook_url})
        print(f"📡 Webhook setup status: {res.status_code} {res.text}")
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")

set_webhook_once()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
