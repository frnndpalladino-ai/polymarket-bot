import requests
import time

TOKEN = "..."
CHAT_ID = "..."

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

send("🟢 TEST 1 - BOT ATTIVO")

while True:
    send("🟡 TEST LOOP - BOT VIVO")
    time.sleep(30)