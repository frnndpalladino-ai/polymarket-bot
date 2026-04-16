import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10))
# Intervallo più lungo per "calmare" l'API
CHECK_INTERVAL = 60 

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print("--- BOT DEFINITIVO OPERATIVO ---", flush=True)
    send_msg("✅ *Bot Operativo*\nInizio monitoraggio con protezione anti-ban.")
    
    # User-Agent più credibile
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    while True:
        try:
            # Endpoint alternativo meno congestionato
            url = "https://clob.polymarket.com/sampling-markets"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 429:
                print("⚠️ Limite raggiunto (429). Pausa di 2 minuti...", flush=True)
                time.sleep(120)
                continue
                
            if response.status_code == 200:
                data = response.json()
                # Gestione flessibile della risposta (lista o dizionario)
                markets = data.get('markets', data) if isinstance(data, dict) else data
                
                if not markets:
                    print("Lista mercati vuota, riprovo...", flush=True)
                    time.sleep(30)
                    continue

                for m in markets:
                    if not isinstance(m, dict): continue
                    m_id = m.get('condition_id')
                    # Prende il volume da diverse chiavi possibili
                    vol = float(m.get('volume', m.get('adjusted_volume', 0)))
                    
                    if m_id in MARKET_DATA:
                        diff = vol - MARKET_DATA[m_id]
                        if diff >= THRESHOLD:
                            title = m.get('question', 'Market')
                            slug = m.get('market_slug', '')
                            link = f"https://polymarket.com/event/{slug}"
                            
                            msg = f"Link {title}\n{diff:,.0f}\nYes\n{link}"
                            send_msg(msg)
                            print(f"!!! NOTIFICA: {title} +{diff}", flush=True)
                    
                    MARKET_DATA[m_id] = vol
                
                print(f"Scansione effettuata. Monitorando {len(MARKET_DATA)} mercati.", flush=True)
            
        except Exception as e:
            print(f"Errore: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
