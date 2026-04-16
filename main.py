import os
import requests
import time
import re

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

WHALE_THRESHOLD = 1000  # cambia dopo test

seen_trades = set()
market_map = {}

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
# API
# =========================
def get_trades():
    try:
        return requests.get(
            "https://data-api.polymarket.com/trades",
            timeout=10
        ).json()
    except Exception as e:
        print("Trades API error:", e)
        return []

def get_markets():
    try:
        return requests.get(
            "https://gamma-api.polymarket.com/markets",
            timeout=10
        ).json()
    except Exception as e:
        print("Markets API error:", e)
        return []

# =========================
# LINK
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
# LOAD MARKETS MAP
# =========================
def update_market_map():
    global market_map
    markets = get_markets()

    for m in markets:
        mid = m.get("id")
        name = m.get("question", "Unknown")
        url = get_market_url(m)

        if mid:
            market_map[mid] = {
                "name": name,
                "url": url
            }

    print(f"Markets mapped: {len(market_map)}")

# =========================
# START
# =========================
send("🟢 WHALE BOT PRO ATTIVO (TRADES + LINK)")

update_market_map()

# =========================
# LOOP
# =========================
while True:
    try:
        trades = get_trades()

        print(f"Trades fetched: {len(trades)}")

        for t in trades:
            tid = t.get("id")

            if tid in seen_trades:
                continue
            seen_trades.add(tid)

            size = t.get("size") or t.get("amount") or 0
            side = t.get("side", "UNKNOWN")
            market_id = t.get("market") or t.get("conditionId")

            try:
                size = float(size)
            except:
                continue

            if size >= WHALE_THRESHOLD:

                # direzione reale
                if side.lower() == "buy":
                    direction = "🟢 YES (buy)"
                elif side.lower() == "sell":
                    direction = "🔴 NO (sell)"
                else:
                    direction = "⚪ UNKNOWN"

                # nome + link
                market_info = market_map.get(market_id, {})
                name = market_info.get("name", "Unknown Market")
                url = market_info.get("url", "")

                send(f"""🐋 REAL WHALE TRADE

📊 {name}

💰 Size: ${round(size,2)}
🎯 Side: {direction}

🔗 {url}
""")

        # aggiorna mercati ogni tanto
        if int(time.time()) % 300 < 5:
            update_market_map()

        time.sleep(5)

    except Exception as e:
        send(f"❌ ERROR: {e}")
        time.sleep(10)