import requests
import time
import os

# Configurazione tramite variabili d'ambiente (per sicurezza su Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 50000))  # Default 50k se non specificato
CHECK_INTERVAL = 30  # Secondi tra i controlli

MARKET_DATA = {}

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def get_markets():
    # API di Polymarket per i mercati attivi
    url = "https://clob.polymarket.com/markets"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return []
    return []

def monitor():
    print("Bot avviato e in ascolto...")
    while True:
        markets = get_markets()
        
        for market in markets:
            m_id = market.get('condition_id')
            if not m_id: continue
            
            # Volume attuale
            current_volume = float(market.get('volume', 0))
            title = market.get('question', 'Mercato senza titolo')
            slug = market.get('market_slug', '')
            
            # Se è la prima volta che vediamo il mercato, lo salviamo e basta
            if m_id in MARKET_DATA:
                prev_volume = MARKET_DATA[m_id]
                diff = current_volume - prev_volume
                
                if diff >= THRESHOLD:
                    # Costruzione link e messaggio
                    link = f"https://polymarket.com/event/{slug}"
                    # Nota: Il lato (Yes/No) non è presente nel volume aggregato.
                    # Per semplicità indichiamo che c'è stato un forte ingresso.
                    msg = f"Link {title}\n[{link}]({link})\n\n💰 *Ingresso:* ${diff:,.2f}\n🎯 *Esito:* Rilevato movimento"
                    send_telegram_msg(msg)
            
            MARKET_DATA[m_id] = current_volume
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
