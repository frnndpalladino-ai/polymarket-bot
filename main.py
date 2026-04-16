import os
import requests
import time
import re

# =========================
# CONFIG
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

VOLUME_THRESHOLD = 500  # 🔥 test basso → poi alza a 3000+

seen_volume = {}
seen_price = {}

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
send("🟢 WHALE BOT LIVE (REAL VOLUME MODE)")

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
# PRICE EXTRACTION
# =========================
def extract_price(m):
    try:
        if "outcomePrices" in m and m["outcomePrices"]:
            return float(m["outcomePrices"][0])

        if m.get("lastTradePrice"):
            return float(m["lastTradePrice"])

        if m.get("price"):
            return float(m["price"])
    except:
        pass

    return 0.0

# =========================
# SLUG / LINK
# =========================
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9 ]', '', text)
    text = text.replace(" ", "-")
    return text[:80]

def get_market_url(m):
    slug = m.get("slug")

    if slug:
        return f"https://polymarket.com/market/{slug}"

    name = m.get("question", "")
    return f"https://polymarket.com/market/{slugify(name)}"

# =========================
# LOOP PRINCIPALE
# =========================
while True:
    try:
        markets = get_markets()

        print(f"Markets: {len(markets)}")

        for m in markets:
            mid = m.get("id")
            name = m.get("question", "Unknown")

            volume = m.get("volume") or 0  # 🔥 FIX PRINCIPALE
            price = extract_price(m)

            try:
                volume = float(volume)
                price = float(price)
            except:
                continue

            # debug
            print("DEBUG:", name[:40], "VOL:", volume, "PRICE:", price)

            if mid is None or price == 0:
                continue

            # inizializzazione
            if mid not in seen_volume:
                seen_volume[mid] = volume
                seen_price[mid] = price
                continue

            old_volume = seen_volume[mid]
            old_price = seen_price[mid]

            delta_volume = volume - old_volume
            delta_price = price - old_price

            # 🐋 WHALE DETECTION
            if delta_volume >= VOLUME_THRESHOLD:

                if delta_price > 0:
                    side = "🟢 YES (bullish)"
                elif delta_price < 0:
                    side = "🔴 NO (bearish)"
                else:
                    side = "⚪ NEUTRAL"

                url = get_market_url(m)

                send(f"""🐋 WHALE MONEY DETECTED

📊 {name}

💰 Money In: +${round(delta_volume,2)}
📈 Price: {round(old_price,3)} → {round(price,3)}

🎯 Side: {side}

🔗 {url}
""")

            seen_volume[mid] = volume
            seen_price[mid] = price

        time.sleep(10)

    except Exception as e:
        send(f"❌ LOOP ERROR: {e}")
        time.sleep(10)