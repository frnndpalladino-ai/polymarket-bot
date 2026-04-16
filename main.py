import requests
import time
import os
import sys

# Configurazione Ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10)) # Mantengo 10 per il test, modificalo su Render quando vuoi
MIN_MARKET_VOL = 1000 # Filtro: monitora solo mercati con volume totale > 1000$
CHECK_INTERVAL = 35 

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print(f"--- SCANNER AVVIATO (Filtro Mercati: >${MIN_MARKET_VOL}) ---")
    send_msg(f"🚀 *Bot Online*\nFiltro mercati attivi: >${MIN_MARKET_VOL}\nSoglia alert: ${THRESHOLD}")
    
    while True:
        try:
            # Chiamata all'API dei mercati
            response = requests.get("https://clob.polymarket.com/markets", timeout=30)
            if response.status_code != 200:
                print(f"Errore API: {response.status_code}")
                time.sleep(60)
                continue
                
            markets = response.json()
            if not isinstance(markets, list): continue

            processed_count = 0
            for m in markets:
                vol = float(m.get('volume', 0))
                
                # Applichiamo il filtro richiesto
                if vol < MIN_MARKET_VOL:
                    continue
                
                m_id = m.get('condition_id')
                if not m_id: continue
                
                processed_count += 1
                
                # Se abbiamo già questo mercato in memoria, calcoliamo la differenza
                if m_id in MARKET_DATA:
                    diff = vol - MARKET_DATA[m_id]
                    
                    if diff >= THRESHOLD:
                        title = m.get('question', 'Market')
                        slug = m.get('market_slug', '')
                        link = f"https://polymarket.com/event/{slug}"
                        
                        # Formato richiesto
                        msg = (
                            f"Link {title}\n"
                            f"{diff:,.0f}\n"
                            f"Yes\n" # Nota: Indica un ingresso, l'esito specifico richiede analisi trades
                            f"{link}"
                        )
                        send_msg(msg)
                        print(f"Alert inviato per {title} (+{diff})")
                
                # Aggiorniamo sempre il volume attuale
                MARKET_DATA[m_id] = vol

            print(f"Scansione completata. Mercati rilevanti monitorati: {processed_count}")
            
        except Exception as e:
            print(f"Errore ciclo: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Mancano configurazioni!")
        sys.exit(1)
    monitor()
