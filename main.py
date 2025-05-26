from fastapi import FastAPI, Request
import os
import json
from dotenv import load_dotenv
from tasks import process_update_background
import telebot
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import gspread
from datetime import datetime
import os
from zoneinfo import ZoneInfo


load_dotenv()
app = FastAPI()

BOT_TOKEN = os.getenv("TELE_TOKEN")
print("📢 Loaded BOT_TOKEN:", BOT_TOKEN)

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    print("🚨 Incoming Telegram webhook hit!")  # <- top level
    try:
        body = await request.body()
        print("📦 Raw body:", body.decode("utf-8")[:100])  # preview only
        process_update_background.delay(body.decode("utf-8"))
        return {"ok": True}
    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        return {"error": str(e)}


