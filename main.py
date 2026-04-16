import os
import requests
import time

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

VOLUME_THRESHOLD = 5000  # modifica se vuoi

seen_volume = {}
seen_price = {}

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

# estrai prezzo robusto
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
    return 0

send("🟢 WHALE BOT CON DIREZIONE ATTIVO")

while True:
    try:
        markets = get_markets()

        for m in markets:
            mid = m.get("id")
            name = m.get("question", "Unknown")

            volume = m.get("volume24hr") or 0
            price = extract_price(m)

            try:
                volume = float(volume)
                price = float(price)
            except:
                continue

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

            # 🐋 whale detection
            if delta_volume >= VOLUME_THRESHOLD:

                if delta_price > 0:
                    side = "🟢 YES (bullish)"
                elif delta_price < 0:
                    side = "🔴 NO (bearish)"
                else:
                    side = "⚪ NEUTRAL"

                send(f"""🐋 WHALE MONEY + DIRECTION

📊 {name}

💰 Money In: +${round(delta_volume,2)}
📈 Price: {round(old_price,3)} → {round(price,3)}

🎯 Side: {side}
""")

            seen_volume[mid] = volume
            seen_price[mid] = price

        time.sleep(15)

    except Exception as e:
        send(f"❌ ERROR: {e}")
        time.sleep(10)