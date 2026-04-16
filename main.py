import requests
import time
import os
import sys

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10)) 
MIN_MARKET_VOL = 1000 
# Alziamo il tempo di attesa per non farci bannare (45-60 secondi è più sicuro)
CHECK_INTERVAL = 50 

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print("--- AVVIO SCANNER V5 (ANTI-BLOCK) ---", flush=True)
    send_msg("🛡️ *Bot Online (V5)*\nModalità prudente attivata per evitare blocchi.")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    while True:
        try:
            print(f"Richiesta dati... {time.strftime('%H:%M:%S')}", flush=True)
            # Cambiamo endpoint: questo è quello usato dal sito ufficiale per caricare i mercati
            url = "https://clob.polymarket.com/sampling-markets" 
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 429:
                print("⚠️ Blocco 429 rilevato. Aspetto 2 minuti...", flush=True)
                time.sleep(120)
                continue
                
            if response.status_code != 200:
                print(f"Errore API: {response.status_code}", flush=True)
                time.sleep(60)
                continue
                
            markets = response.json()
            # Se l'API restituisce un dizionario invece di una lista, proviamo a estrarre i dati
            if isinstance(markets, dict):
                markets = markets.get('markets', markets.get('data', []))

            if not isinstance(markets, list) or len(markets) < 10:
                print(f"Dati non validi ricevuti (L: {len(markets) if isinstance(markets, list) else 'NaN'})", flush=True)
                time.sleep(60)
                continue

            print(f"Ricevuti {len(markets)} mercati.", flush=True)

            for m in markets:
                if not isinstance(m, dict): continue
                
                # In questo endpoint il volume potrebbe chiamarsi in modo diverso
                vol = float(m.get('volume', m.get('adjusted_volume', 0)))
                if vol < MIN_MARKET_VOL: continue
                
                m_id = m.get('condition_id')
                if not m_id: continue
                
                if m_id in MARKET_DATA:
                    diff = vol - MARKET_DATA[m_id]
                    if diff >= THRESHOLD:
                        title = m.get('question', 'Market')
                        slug = m.get('market_slug', '')
                        link = f"https://polymarket.com/event/{slug}"
                        
                        msg = f"Link {title}\n{diff:,.0f}\nYes\n{link}"
                        send_msg(msg)
                        print(f"!!! ALERT: {title} (+{diff})", flush=True)
                
                MARKET_DATA[m_id] = vol

        except Exception as e:
            print(f"Errore: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
