import os
import requests
import time

# =========================
# CONFIG (Render ENV)
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# soglia movimento (5% = 0.05)
MOVE_THRESHOLD = 0.02

seen = {}

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        print("SEND:", msg)
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg}
        )
    except Exception as e:
        print("Telegram error:", e)

# =========================
# TEST START
# =========================
send("🟢 BOT AVVIATO SU RENDER - TEST OK")

# =========================
# API
# =========================
def get_markets():
    try:
        return requests.get(
            "https://gamma-api.polymarket.com/markets",
            timeout=10
        ).json()
    except Exception as e:
        print("API error:", e)
        return []

# =========================
# LOOP PRINCIPALE
# =========================
while True:
    try:
        markets = get_markets()

        print(f"Markets fetched: {len(markets)}")

        for m in markets:
            mid = m.get("id")
            name = m.get("question", "Unknown")

            # fallback price fields
            price = (
                m.get("lastTradePrice") or
                m.get("price") or
                0
            )

            try:
                price = float(price)
            except:
                continue

            if price == 0 or mid is None:
                continue

            # prima volta: salva
            if mid not in seen:
                seen[mid] = price
                continue

            old_price = seen[mid]
            change = abs(price - old_price)

            # ALERT
            if change >= MOVE_THRESHOLD:
                send(f"""🐋 MARKET MOVE DETECTED

📊 Market:
{name}

📈 {old_price} → {price}
⚡ Change: {round(change * 100, 2)}%
""")

            seen[mid] = price

        time.sleep(10)

    except Exception as e:
        send(f"❌ LOOP ERROR: {e}")
        time.sleep(10)