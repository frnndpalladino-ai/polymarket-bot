import requests
import time
import os

# Configurazione tramite variabili d'ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# Soglia abbassata a 100 per il test
THRESHOLD = float(os.getenv("THRESHOLD", 100)) 
CHECK_INTERVAL = 30 

MARKET_DATA = {}

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text, 
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Invio Telegram: {response.status_code}")
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def get_markets():
    # Usiamo l'endpoint che include più dettagli
    url = "https://clob.polymarket.com/markets"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
        print(f"Errore API Polymarket: Status {response.status_code}")
    except Exception as e:
        print(f"Errore connessione API: {e}")
    return []

def monitor():
    # MESSAGGIO DI TEST ALL'AVVIO
    print("Inviando messaggio di avvio...")
    send_telegram_msg("✅ **Bot Monitoraggio Polymarket Attivo!**\nSoglia attuale: " + str(THRESHOLD) + " USD")
    
    print("Inizio scansione mercati...")
    
    while True:
        markets = get_markets()
        print(f"Scansione effettuata su {len(markets)} mercati.")
        
        for market in markets:
            if not isinstance(market, dict):
                continue
                
            m_id = market.get('condition_id')
            if not m_id:
                continue
            
            try:
                # Volume totale storico del mercato
                current_volume = float(market.get('volume', 0))
                title = market.get('question', 'Mercato senza titolo')
                slug = market.get('market_slug', '')
                
                if m_id in MARKET_DATA:
                    prev_volume = MARKET_DATA[m_id]
                    diff = current_volume - prev_volume
                    
                    # Se il volume è aumentato più della soglia
                    if diff >= THRESHOLD:
                        link = f"https://polymarket.com/event/{slug}"
                        msg = (
                            f"🔔 *GRANDE MOVIMENTO RILEVATO*\n\n"
                            f"📍 *Mercato:* {title}\n"
                            f"💰 *Denaro inserito:* ${diff:,.2f}\n"
                            f"🔗 [VAI AL MERCATO]({link})"
                        )
                        send_telegram_msg(msg)
                
                # Aggiorna il valore locale per il prossimo confronto
                MARKET_DATA[m_id] = current_volume
                
            except Exception as e:
                continue
            
        # Aspetta prima del prossimo giro
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Verifica che le variabili siano caricate
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERRORE: Variabili TELEGRAM_TOKEN o CHAT_ID mancanti!")
    else:
        monitor()
