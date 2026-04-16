import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
# SOGLIA A 1 PER IL TEST
THRESHOLD = float(os.getenv("THRESHOLD", 1)) 
CHECK_INTERVAL = 40 

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print("--- TEST NOTIFICHE IN CORSO ---", flush=True)
    send_msg("🧪 *Test in corso: Soglia 1$*")
    
    headers = {"User-Agent": "Mozilla/5.0 Chrome/119.0.0.0 Safari/537.36"}
    
    while True:
        try:
            # Usiamo l'endpoint che ti ha dato i 1000 mercati (quello funzionante)
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
                            
                            # Esempio esatto come richiesto
                            msg = f"Link {title}\n{diff:,.2f}\nYes\n{link}"
                            send_msg(msg)
                            print(f"NOTIFICA INVIATA: {diff}$ su {title}", flush=True)
                    
                    MARKET_DATA[m_id] = vol
                
                print(f"Scansione ok alle {time.strftime('%H:%M:%S')}. In attesa di movimenti...", flush=True)
            else:
                print(f"Errore API: {response.status_code}", flush=True)

        except Exception as e:
            print(f"Errore: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
