import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


JSON_TOKEN = os.getenv('JSON_PATHNAME')

with open(JSON_TOKEN, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

with open("credentials.txt", "w") as out:
    out.write(encoded)

print("✅ credentials.txt generated")