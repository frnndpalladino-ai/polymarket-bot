import requests
import time
import os

# Configurazione Ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 50000)) # Torna a 50k o quella che preferisci
CHECK_INTERVAL = 45 # Tempo ideale per non essere bannati

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print("--- BOT DEFINITIVO OPERATIVO ---", flush=True)
    send_msg(f"✅ *Bot Monitoraggio Balene Attivo*\nSoglia attuale: ${THRESHOLD:,.0f}")
    
    headers = {"User-Agent": "Mozilla/5.0 Chrome/119.0.0.0 Safari/537.36"}
    
    while True:
        try:
            # Endpoint stabile testato nei log
            url = "https://clob.polymarket.com/sampling-markets" 
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                markets = response.json()
                if isinstance(markets, dict):
                    markets = markets.get('markets', [])

                for m in markets:
                    m_id = m.get('condition_id')
                    vol = float(m.get('volume', m.get('adjusted_volume', 0)))
                    
                    if m_id in MARKET_DATA:
                        diff = vol - MARKET_DATA[m_id]
                        
                        if diff >= THRESHOLD:
                            title = m.get('question', 'Market')
                            slug = m.get('market_slug', '')
                            link = f"https://polymarket.com/event/{slug}"
                            
                            # Messaggio pulito come da tua richiesta
                            msg = f"Link {title}\n{diff:,.0f}\nYes\n{link}"
                            send_msg(msg)
                            print(f"BALENA RILEVATA: {diff}$ su {title}", flush=True)
                    
                    # Aggiorna lo stato dei volumi
                    MARKET_DATA[m_id] = vol
                
                print(f"Scansione effettuata con successo. Monitorando {len(markets)} mercati.", flush=True)
            else:
                print(f"Errore API: {response.status_code}", flush=True)

        except Exception as e:
            print(f"Errore nel ciclo: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
