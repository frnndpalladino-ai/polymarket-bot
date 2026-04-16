import requests
import time
import os
import sys

# Caricamento Variabili d'Ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10))  # Soglia test
CHECK_INTERVAL = 30 

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Errore invio Telegram: {e}")
        return False

def monitor():
    print("Inizializzazione bot...")
    
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Mancano le variabili d'ambiente! Chiudo.")
        sys.exit(1)

    send_msg("🚀 *Bot in linea!*\nControllo mercati in corso...")
    
    MARKET_DATA = {}
    
    while True:
        try:
            # Chiamata API Polymarket
            response = requests.get("https://clob.polymarket.com/markets", timeout=20)
            
            if response.status_code != 200:
                print(f"Errore API Polymarket: {response.status_code}")
                time.sleep(60)
                continue
                
            markets = response.json()
            
            # Se la lista è valida
            if isinstance(markets, list):
                print(f"Scansione di {len(markets)} mercati...")
                
                for m in markets:
                    if not isinstance(m, dict): continue
                    
                    m_id = m.get('condition_id')
                    vol = float(m.get('volume', 0))
                    
                    if m_id in MARKET_DATA:
                        old_vol = MARKET_DATA[m_id]
                        diff = vol - old_vol
                        
                        if diff >= THRESHOLD:
                            title = m.get('question', 'Market')
                            slug = m.get('market_slug', '')
                            link = f"https://polymarket.com/event/{slug}"
                            
                            alert = (
                                f"🔔 *MOVIMENTO RILEVATO*\n"
                                f"📍 {title}\n"
                                f"💰 +${diff:,.2f}\n"
                                f"🔗 [Link Mercato]({link})"
                            )
                            send_msg(alert)
                    
                    # Salva il volume attuale
                    MARKET_DATA[m_id] = vol
            
        except Exception as e:
            print(f"Errore nel ciclo: {e}")
            time.sleep(10) # Aspetta prima di riprovare
            
        # Pausa tra le scansioni
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
