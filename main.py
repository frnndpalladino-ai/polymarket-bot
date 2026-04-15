import os
import requests
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

VOLUME_THRESHOLD = 10000  # soldi entrati (modifica dopo test)

seen_volume = {}

def send(msg):
    try:
        print("SEND:", msg)
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except Exception as e:
        print("Telegram error:", e)

def get_markets():
    try:
        return requests.get("https://gamma-api.polymarket.com/markets").json()
    except:
        return []

send("🟢 BOT WHALE VOLUME ATTIVO")

while True:
    try:
        markets = get_markets()

        for m in markets:
            mid = m.get("id")
            name = m.get("question", "Unknown")

            volume = m.get("volume24hr") or 0

            try:
                volume = float(volume)
            except:
                continue

            if mid not in seen_volume:
                seen_volume[mid] = volume
                continue

            old_volume = seen_volume[mid]
            delta = volume - old_volume

            # 🐋 QUI RILEVIAMO I SOLDI VERI
            if delta >= VOLUME_THRESHOLD:
                send(f"""🐋 WHALE MONEY DETECTED

📊 {name}

💰 New money: +${round(delta,2)}
📈 24h Volume: ${round(volume,2)}
""")

            seen_volume[mid] = volume

        time.sleep(15)

    except Exception as e:
        send(f"❌ ERROR: {e}")
        time.sleep(10)