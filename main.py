import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10))
CHECK_INTERVAL = 60 # Aumentiamo a 60s per evitare il ban

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print("--- SCANNER V7: MODALITÀ BYPASS ---", flush=True)
    send_msg("🛠️ *Sincronizzazione V7 avviata...*")
    
    # Header più simili a un browser reale
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Origin": "https://polymarket.com",
        "Referer": "https://polymarket.com/"
    }
    
    while True:
        try:
            # Nuovo Endpoint più leggero
            url = "https://clob.polymarket.com/markets/simplified" 
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Errore API {response.status_code}. Attendo...", flush=True)
                time.sleep(120) # Se c'è errore, aspetta 2 minuti
                continue
                
            markets = response.json()
            
            # Verifichiamo la struttura (può essere una lista o un dict con chiave 'data')
            if isinstance(markets, dict):
                markets = markets.get('data', [])
            
            if not markets or len(markets) < 5:
                print("Dati ancora insufficienti. Polymarket sta limitando l'IP.", flush=True)
                time.sleep(60)
                continue

            print(f"Dati ricevuti con successo: {len(markets)} mercati.", flush=True)

            for m in markets:
                m_id = m.get('condition_id')
                # Cerchiamo il volume in diverse chiavi possibili
                vol = float(m.get('volume', m.get('usd_volume', 0)))
                
                if m_id and m_id in MARKET_DATA:
                    diff = vol - MARKET_DATA[m_id]
                    if diff >= THRESHOLD:
                        title = m.get('question', 'Mercato')
                        slug = m.get('market_slug', m.get('slug', ''))
                        link = f"https://polymarket.com/event/{slug}"
                        
                        msg = f"Link {title}\n{diff:,.0f}\nYes\n{link}"
                        send_msg(msg)
                        print(f"Notifica inviata: {title}", flush=True)
                
                if m_id:
                    MARKET_DATA[m_id] = vol

        except Exception as e:
            print(f"Errore tecnico: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
