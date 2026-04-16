import requests
import time
import os
import sys

# Configurazione Ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10)) 
MIN_MARKET_VOL = 1000 
CHECK_INTERVAL = 30 

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    # Il flush=True serve per vedere i log subito su Render
    print("--- INIZIALIZZAZIONE SCANNER V4 ---", flush=True)
    send_msg("🚀 *Bot Online: Fase di acquisizione dati...*")
    
    # User-Agent per evitare blocchi dall'API
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    while True:
        try:
            print(f"Richiesta dati a Polymarket... ({time.strftime('%H:%M:%S')})", flush=True)
            response = requests.get("https://clob.polymarket.com/markets", headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Errore API: {response.status_code}", flush=True)
                time.sleep(60)
                continue
                
            markets = response.json()
            total_raw = len(markets)
            print(f"Dati ricevuti. Mercati totali nell'API: {total_raw}", flush=True)

            processed_count = 0
            for m in markets:
                vol = float(m.get('volume', 0))
                
                # Filtro volume minimo
                if vol < MIN_MARKET_VOL:
                    continue
                
                m_id = m.get('condition_id')
                if not m_id: continue
                
                processed_count += 1
                
                if m_id in MARKET_DATA:
                    diff = vol - MARKET_DATA[m_id]
                    
                    if diff >= THRESHOLD:
                        title = m.get('question', 'Market')
                        slug = m.get('market_slug', '')
                        link = f"https://polymarket.com/event/{slug}"
                        
                        msg = f"Link {title}\n{diff:,.0f}\nYes\n{link}"
                        send_msg(msg)
                        print(f"!!! ALERT INVIATO: {title} (+{diff})", flush=True)
                
                MARKET_DATA[m_id] = vol

            print(f"Scansione completata. Monitorando {processed_count} mercati attivi.", flush=True)
            
        except Exception as e:
            print(f"ERRORE NEL CICLO: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERRORE: Variabili Ambiente mancanti!", flush=True)
        sys.exit(1)
    monitor()
