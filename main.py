import requests
import time
import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

WHALE_THRESHOLD = 15000

seen = set()

def send(msg):
    if not TOKEN or not CHAT_ID:
        print("WARNING: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set. Message not sent.")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg},
            timeout=10
            
        send("🟢 BOT ONLINE - Render avviato correttamente")
        )
    except Exception as e:
        print(f"Telegram send error: {e}")

def get_trades():
    url = "https://data-api.polymarket.com/trades"
    return requests.get(url, timeout=15).json()

while True:
    try:
        trades = get_trades()

        for t in trades:
            trade_id = t.get("transactionHash")

            if not trade_id or trade_id in seen:
                continue
            seen.add(trade_id)

            size = float(t.get("size", 0))
            side = t.get("side", "UNKNOWN")
            market_name = t.get("title", "Unknown Market")

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
