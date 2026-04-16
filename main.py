import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = 3600 # 1 ora esatta

MARKET_DATA = {}

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        # Usiamo MarkdownV2 o lasciamo semplice per evitare errori con caratteri speciali
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}, timeout=15)
    except Exception as e:
        print(f"Errore Telegram: {e}")

def get_gamma_markets():
    headers = {"User-Agent": "Mozilla/5.0"}
    # Recuperiamo un numero alto di mercati per essere sicuri di coprire tutto
    url = "https://gamma-api.polymarket.com/markets?active=true&limit=1000"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def monitor():
    print("--- MONITORAGGIO ORARIO AVVIATO (TOP 50) ---", flush=True)
    send_msg("📊 Report Orario Attivo: riceverai la lista dei 50 mercati più movimentati ogni ora.")
    
    while True:
        markets = get_gamma_markets()
        current_time = time.strftime('%H:%M')
        
        if not markets:
            print(f"[{current_time}] Errore recupero dati. Riprovo al prossimo ciclo.", flush=True)
        else:
            movers = []
            
            for m in markets:
                m_id = m.get('conditionId')
                vol = float(m.get('volume', 0))
                title = m.get('question', 'Unknown')
                slug = m.get('slug', '')
                
                if m_id in MARKET_DATA:
                    diff = vol - MARKET_DATA[m_id]
                    if diff > 0:
                        movers.append({
                            'title': title,
                            'diff': diff,
                            'link': f"https://polymarket.com/event/{slug}"
                        })
                
                # Aggiorna lo storico
                MARKET_DATA[m_id] = vol

            # Se abbiamo dati precedenti, inviamo la classifica
            if movers:
                # Ordina per differenza di volume decrescente
                movers.sort(key=lambda x: x['diff'], reverse=True)
                top_50 = movers[:50]
                
                report = f"🏆 TOP 50 MOVEMENTS (Ultima ora - {current_time})\n\n"
                for i, m in enumerate(top_50, 1):
                    line = f"{i}. {m['title']}\n💰 +${m['diff']:,.0f}\n🔗 {m['link']}\n\n"
                    
                    # Telegram ha un limite di 4096 caratteri per messaggio
                    if len(report) + len(line) > 4000:
                        send_msg(report)
                        report = ""
                    report += line
                
                if report:
                    send_msg(report)
                print(f"[{current_time}] Report inviato.", flush=True)
            else:
                print(f"[{current_time}] Primo ciclo completato. Dati memorizzati.", flush=True)

        # Attendi 1 ora
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
