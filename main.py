from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
from bot import process_update_from_webhook
import uvicorn
import requests
import base64

load_dotenv()

app = FastAPI()

BOT_TOKEN = os.getenv("TELE_TOKEN")
print("📢 Loaded BOT_TOKEN:", BOT_TOKEN[:10] + "..." if BOT_TOKEN else "None")

# Setup Google Sheets credentials for Cloud Run
def setup_google_credentials():
    # Check if running on Cloud Run (has GOOGLE_CREDS_BASE64)
    if os.getenv("GOOGLE_CREDS_BASE64"):
        print("🔧 Setting up Google credentials from environment...")
        with open("credentials.json", "wb") as f:
            f.write(base64.b64decode(os.getenv("GOOGLE_CREDS_BASE64")))
        print("✅ Google credentials file created")
    elif os.path.exists("credentials.json"):
        print("✅ Found local credentials.json file")
    else:
        print("⚠️ No Google credentials found")

# Setup credentials on startup
setup_google_credentials()

@app.get("/")
def root():
    print("✅ Health check hit!")
    return {"message": "Telegram Bot is running on Cloud Run!", "status": "healthy"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "bot_token_set": bool(BOT_TOKEN)}

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    print("🚨 Incoming Telegram webhook hit!")
    try:
        body = await request.body()
        print("📦 Processing webhook...")
        process_update_from_webhook(body.decode("utf-8"))
        return {"ok": True}
    except Exception as e:
        print("❌ Error processing webhook:", str(e))
        return {"error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Set webhook when the service starts"""
    print("🚀 Starting up...")
    
    # Get the service URL from Cloud Run metadata (if available)
    try:
        # Try to get Cloud Run service URL
        import requests
        metadata_server = "http://metadata.google.internal/computeMetadata/v1/"
        metadata_flavor = {"Metadata-Flavor": "Google"}
        
        # Get project ID
        project_response = requests.get(
            metadata_server + "project/project-id",
            headers=metadata_flavor,
            timeout=5
        )
        project_id = project_response.text
        
        # Get service name and region from environment or defaults
        service_name = os.getenv("K_SERVICE", "telegram-bot")
        region = os.getenv("FUNCTION_REGION", "asia-southeast-1")
        
        # Construct Cloud Run URL
        webhook_url = f"https://{service_name}-{project_id}.a.run.app"
        
    except Exception as e:
        print(f"⚠️ Could not get Cloud Run URL from metadata: {e}")
        # Fallback to environment variable
        webhook_url = os.getenv("WEBHOOK_URL")
    
    if webhook_url and BOT_TOKEN:
        full_webhook_url = f"{webhook_url}/{BOT_TOKEN}"
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
                json={"url": full_webhook_url},
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ Webhook set successfully: {full_webhook_url}")
            else:
                print(f"❌ Failed to set webhook: {response.text}")
        except Exception as e:
            print(f"❌ Error setting webhook: {e}")
    else:
        print("⚠️ Missing WEBHOOK_URL or BOT_TOKEN")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting server on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port)