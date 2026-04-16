import requests
import time
import os

# Configurazione tramite variabili d'ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 50000))
CHECK_INTERVAL = 30 

MARKET_DATA = {}

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def get_markets():
    url = "https://clob.polymarket.com/markets"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # Verifichiamo che i dati siano effettivamente una lista
            if isinstance(data, list):
                return data
            else:
                print(f"Formato dati inatteso: {type(data)}")
                return []
    except Exception as e:
        print(f"Errore API Polymarket: {e}")
        return []
    return []

def monitor():
    print("Bot avviato e in ascolto...")
    while True:
        markets = get_markets()
        
        for market in markets:
            # Controllo di sicurezza: se 'market' non è un dizionario, lo saltiamo
            if not isinstance(market, dict):
                continue
                
            m_id = market.get('condition_id')
            if not m_id:
                continue
            
            try:
                current_volume = float(market.get('volume', 0))
                title = market.get('question', 'Mercato senza titolo')
                slug = market.get('market_slug', '')
                
                if m_id in MARKET_DATA:
                    prev_volume = MARKET_DATA[m_id]
                    diff = current_volume - prev_volume
                    
                    if diff >= THRESHOLD:
                        link = f"https://polymarket.com/event/{slug}"
                        msg = f"🔗 *Link:* [{title}]({link})\n💰 *Ingresso:* ${diff:,.2f}\n📈 *Volume Tot:* ${current_volume:,.2f}"
                        send_telegram_msg(msg)
                
                MARKET_DATA[m_id] = current_volume
            except (ValueError, TypeError) as e:
                # Salta mercati con dati corrotti o volumi non numerici
                continue
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
