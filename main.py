import requests
import time
import os

# CARICAMENTO VARIABILI
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THRESHOLD = float(os.getenv("THRESHOLD", 100))
CHECK_INTERVAL = 30 

def monitor():
    # DEBUG LOGS (Controlliamo cosa vede Render)
    print("--- DEBUG VARIABILI ---")
    print(f"TOKEN trovato: {'SI' if TELEGRAM_TOKEN else 'NO'}")
    if TELEGRAM_TOKEN:
        print(f"Inizio TOKEN: {TELEGRAM_TOKEN[:5]}***")
    print(f"CHAT_ID trovato: {'SI' if CHAT_ID else 'NO'}")
    if CHAT_ID:
        print(f"Valore CHAT_ID: {CHAT_ID}")
    print("-----------------------")

    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("ERRORE CRITICO: Variabili ancora mancanti. Controlla la tab Environment su Render!")
        return

    # Se arriviamo qui, le variabili ci sono
    url_test = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "✅ Test Connessione: Bot Partito!"}
    
    try:
        r = requests.post(url_test, json=payload)
        print(f"Risposta Telegram: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Errore invio: {e}")

    MARKET_DATA = {}
    print("Inizio scansione mercati...")

    while True:
        try:
            response = requests.get("https://clob.polymarket.com/markets", timeout=15)
            markets = response.json()
            
            for market in markets:
                if not isinstance(market, dict): continue
                m_id = market.get('condition_id')
                vol = float(market.get('volume', 0))
                
                if m_id in MARKET_DATA:
                    diff = vol - MARKET_DATA[m_id]
                    if diff >= THRESHOLD:
                        slug = market.get('market_slug', '')
                        title = market.get('question', 'Market')
                        link = f"https://polymarket.com/event/{slug}"
                        msg = f"Link {title}\n{diff:,.0f}\nTarget Detectato\n{link}"
                        requests.post(url_test, json={"chat_id": CHAT_ID, "text": msg})
                
                MARKET_DATA[m_id] = vol
        except Exception as e:
            print(f"Errore durante il ciclo: {e}")
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
