import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 10))
# Intervallo aumentato a 70 secondi per uscire dal ban
CHECK_INTERVAL = 70 

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}, timeout=10)
    except:
        pass

def monitor():
    print("--- SCANNER V6: MODALITÀ GHOST ---", flush=True)
    send_msg("👻 *Scanner V6 Attivo*\nTentativo di bypass Rate Limit in corso...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    while True:
        try:
            # Usiamo l'endpoint semplificato che restituisce solo i mercati con attività reale
            url = "https://clob.polymarket.com/markets"
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 429:
                print("⚠️ Ancora 429. Mi fermo per 3 minuti...", flush=True)
                time.sleep(180)
                continue
                
            markets = response.json()
            # Se l'API restituisce un errore testuale o lista vuota
            if not isinstance(markets, list) or len(markets) < 5:
                print(f"Ricevuti dati insufficienti ({len(markets) if isinstance(markets, list) else 'ERR'}). Attendo...", flush=True)
                time.sleep(60)
                continue

            count = 0
            for m in markets:
                m_id = m.get('condition_id')
                # Usiamo 'volume_24h' se disponibile, altrimenti 'volume'
                vol = float(m.get('volume', 0))
                
                if m_id and vol > 0:
                    if m_id in MARKET_DATA:
                        diff = vol - MARKET_DATA[m_id]
                        if diff >= THRESHOLD:
                            title = m.get('question', 'Market')
                            slug = m.get('market_slug', '')
                            link = f"https://polymarket.com/event/{slug}"
                            
                            msg = f"Link {title}\n{diff:,.0f}\nYes\n{link}"
                            send_msg(msg)
                            print(f"ALERTA: {title}", flush=True)
                    
                    MARKET_DATA[m_id] = vol
                    count += 1
            
            print(f"Scansione riuscita: {count} mercati monitorati.", flush=True)
            
        except Exception as e:
            print(f"Errore: {e}", flush=True)
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
