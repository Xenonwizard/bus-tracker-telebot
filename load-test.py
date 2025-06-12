import requests
import json
import random
import threading
import time

# CONFIGURE THIS
WEBHOOK_URL = "https://bus-tracker-bot-835724524997.asia-southeast1.run.app/7928950540:AAGGct7klfMLaMaJztDv7ZuFTeRKIiMKWIU"  # Replace with your actual endpoint

def simulate_user_session(user_id):
    def send_message(text):
        payload = {
            "update_id": random.randint(1000000, 9999999),
            "message": {
                "message_id": random.randint(1, 1000),
                "from": {"id": user_id, "is_bot": False, "first_name": "User"},
                "chat": {"id": user_id, "first_name": "User", "type": "private"},
                "date": int(time.time()),
                "text": text
            }
        }
        return post_payload(payload)

    def send_callback(data):
        payload = {
            "update_id": random.randint(1000000, 9999999),
            "callback_query": {
                "id": str(random.randint(10000, 99999)),
                "from": {"id": user_id, "first_name": "User", "is_bot": False},
                "message": {
                    "message_id": random.randint(1000, 9999),
                    "chat": {"id": user_id, "type": "private"}
                },
                "data": data
            }
        }
        return post_payload(payload)

    def post_payload(payload):
        try:
            r = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            print(f"[{user_id}] → {payload.get('message', {}).get('text', payload.get('callback_query', {}).get('data', ''))} → {r.status_code}")
            return r.status_code
        except Exception as e:
            print(f"[{user_id}] ❌ Error: {e}")
            return None

    # Simulate user flow with delays
    time.sleep(random.uniform(0.3, 1.0))
    send_message("/start")

    time.sleep(0.8)
    send_message(f"A{random.randint(1, 50)}")  # Bus #

    time.sleep(0.8)
    send_message(str(random.randint(1, 5)))  # Wave

    time.sleep(0.8)
    send_message("NP1, NPG")  # CGs

    time.sleep(0.8)
    send_message(f"SGX{random.randint(1000,9999)}")  # Plate #

    time.sleep(0.8)
    send_message("Alex")  # IC

    time.sleep(0.8)
    send_message("Jamie")  # 2IC

    pax = random.randint(30, 45)
    time.sleep(0.8)
    send_message(str(pax))  # Pax count

    time.sleep(1.0)
    send_callback("confirm_details")  # ✅ Continue

    time.sleep(1.0)
    send_callback("begin_checklist")  # 🟢 Okay

    time.sleep(1.0)
    send_callback("yes_left_star")  # Step 1

    time.sleep(0.5)
    send_message(str(pax))  # Re-enter pax after step

    print(f"[{user_id}] ✅ Finished simulation")

# Launch 27 concurrent simulated users
threads = []
for _ in range(27):
    user_id = random.randint(100000, 999999)
    t = threading.Thread(target=simulate_user_session, args=(user_id,))
    threads.append(t)
    t.start()

# Wait for all to finish
for t in threads:
    t.join()

print("✅ Load test completed: 27 users simulated full flow.")