import os
import requests
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    print("SENDING:", msg)
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

send("🟢 TEST DEFINITIVO - BOT ATTIVO SU RENDER")

while True:
    send("🔄 LOOP ATTIVO")
    time.sleep(20)