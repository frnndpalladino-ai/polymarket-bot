import requests
import time

TOKEN ="8741430524:AAEDYAOHXZSguLE-2grc3QBsn8tRZjD3bG"s
CHAT_ID = "8434401391"

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

send("🟢 TEST 1 - BOT ATTIVO")

while True:
    send("🟡 TEST LOOP - BOT VIVO")
    time.sleep(30)