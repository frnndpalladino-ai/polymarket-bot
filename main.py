import requests
import time

TOKEN = "METTI_TOKEN"
CHAT_ID = "METTI_CHAT_ID"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

# TEST IMMEDIATO
send("🟢 BOT ONLINE - TEST OK")

while True:
    print("bot running...")
    time.sleep(60)