import requests
import time

# =========================
# CONFIG
# =========================
TOKEN = "METTI_IL_TUO_TOKEN"
CHAT_ID = "METTI_IL_TUO_CHAT_ID"

WHALE_THRESHOLD = 15000

seen = set()

# =========================
# TELEGRAM
# =========================
def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

# =========================
# START TEST (IMPORTANTISSIMO)
# =========================
send("🟢 BOT ONLINE - Render avviato correttamente")

# =========================
# API
# =========================
def get_markets():
    try:
        return requests.get("https://gamma-api.polymarket.com/markets").json()
    except:
        return []

def get_trades():
    try:
        return requests.get("https://data-api.polymarket.com/trades").json()
    except:
        return []

# =========================
# LOOP PRINCIPALE
# =========================
while True:
    try:
        markets = get_markets()
        trades = get_trades()

        market_map = {
            m.get("id"): m.get("question", "Unknown Market")
            for m in markets if m.get("id")
        }

        for t in trades:
            trade_id = t.get("id")

            if trade_id in seen:
                continue
            seen.add(trade_id)

            size = float(t.get("amount", t.get("size", 0)))
            market_id = t.get("market", t.get("conditionId"))
            side = t.get("side", "UNKNOWN")

            market_name = market_map.get(market_id, "Unknown Market")

            if size >= WHALE_THRESHOLD:

                msg = f"""
🐋 WHALE ALERT

📊 Market:
{market_name}

💰 Size: ${size}
📈 Side: {side}

⚡ Source: Polymarket flow
"""

                print(msg)
                send(msg)

        time.sleep(8)

    except Exception as e:
        send(f"❌ ERROR: {e}")
        time.sleep(10)
