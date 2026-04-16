import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
        print(f"Risposta Telegram: {r.status_code}", flush=True)
    except Exception as e:
        print(f"Errore Telegram: {e}", flush=True)

def monitor():
    print("--- STRESS TEST: INVIO NOTIFICHE A RAFFICA ---", flush=True)
    send_msg("🔥 *STRESS TEST AVVIATO* 🔥\nRiceverai notifiche per ogni mercato con volume > 0.")
    
    headers = {"User-Agent": "Mozilla/5.0 Chrome/119.0.0.0 Safari/537.36"}
    
    while True:
        try:
            url = "https://clob.polymarket.com/sampling-markets" 
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                markets = response.json()
                if isinstance(markets, dict):
                    markets = markets.get('markets', [])

                # Prendiamo solo i primi 5 mercati per non farti esplodere il telefono
                for m in markets[:5]: 
                    title = m.get('question', 'Market')
                    vol = float(m.get('volume', 0))
                    slug = m.get('market_slug', '')
                    link = f"https://polymarket.com/event/{slug}"
                    
                    msg = f"TEST NOTIFICA\nLink: {title}\nVolume attuale: {vol:,.2f}\n{link}"
                    send_msg(msg)
                    time.sleep(2) # Pausa per non intasare Telegram
                
                print("Primi 5 messaggi inviati. Aspetto 1 minuto...", flush=True)
            else:
                print(f"Errore API: {response.status_code}", flush=True)

        except Exception as e:
            print(f"Errore: {e}", flush=True)
            
        time.sleep(60)

if __name__ == "__main__":
    monitor()
