from celery import Celery
import os
from dotenv import load_dotenv
from bot import process_update_from_webhook

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("tasks", broker=REDIS_URL)

@celery_app.task
def process_update_background(update_json: str):
    print("🎯 Celery is processing update")
    process_update_from_webhook(update_json)