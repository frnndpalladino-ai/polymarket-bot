import os
import requests
import time

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MOVE_THRESHOLD = 0.02  # 2%

seen = {}

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        print("SEND:", msg)
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
    except Exception as e:
        print("Telegram error:", e)

# =========================
# START TEST
# =========================
send("🟢 BOT ONLINE - AVVIATO CORRETTAMENTE")

# =========================
# PRICE EXTRACTOR (FIX CHIAVE)
# =========================
def extract_price(m):
    try:
        if m.get("lastTradePrice"):
            return float(m["lastTradePrice"])

        if m.get("price"):
            return float(m["price"])

        if "outcomePrices" in m and m["outcomePrices"]:
            prices = m["outcomePrices"]
            if isinstance(prices, list):
                return float(prices[0])

    except:
        pass

    return 0

# =========================
# API
# =========================
def get_markets():
    try:
        r = requests.get(
            "https://gamma-api.polymarket.com/markets",
            timeout=10
        )
        return r.json()
    except Exception as e:
        print("API error:", e)
        return []

# =========================
# LOOP PRINCIPALE
# =========================
while True:
    try:
        markets = get_markets()

        print(f"Markets received: {len(markets)}")

        for m in markets:
            mid = m.get("id")
            name = m.get("question", "Unknown")

            price = extract_price(m)

            # debug utile nei log
            print(mid, name[:40], price)

            if price == 0 or mid is None:
                continue

            if mid not in seen:
                seen[mid] = price
                continue

            old_price = seen[mid]
            change = abs(price - old_price)

            if change >= MOVE_THRESHOLD:
                send(f"""🐋 MARKET MOVE

📊 {name}

📈 {old_price} → {price}
⚡ Change: {round(change * 100, 2)}%
""")

            seen[mid] = price

        time.sleep(10)

    except Exception as e:
        send(f"❌ LOOP ERROR: {e}")
        time.sleep(10)