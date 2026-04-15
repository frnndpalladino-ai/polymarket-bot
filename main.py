import requests
import time

TOKEN = "..."
CHAT_ID = "..."

seen = {}

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

def get_markets():
    return requests.get("https://gamma-api.polymarket.com/markets").json()

send("🟢 BOT ATTIVO - monitoring markets")

while True:
    try:
        markets = get_markets()

        for m in markets:
            mid = m.get("id")
            name = m.get("question", "Unknown")

            price = float(m.get("price", 0))

            if mid in seen:
                old = seen[mid]
                change = abs(price - old)

                # 🔥 whale-like move detection
                if change > 0.10:  # 10% move
                    send(f"""🐋 BIG MOVE DETECTED

📊 Market:
{name}

📈 Move: {old} → {price}
⚡ Change: {round(change*100,2)}%
""")

            seen[mid] = price

        time.sleep(10)

    except Exception as e:
        send(f"❌ ERROR: {e}")
        time.sleep(10)