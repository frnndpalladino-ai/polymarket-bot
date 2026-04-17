import requests
import time
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = 3600 # 1 ora

# Memorie volumi globali
VOL_START_1H = {} # Volume all'inizio dell'ora corrente
VOL_START_3H = {} # Volume all'inizio del blocco di 3 ore
ciclo_count = 0

def send_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}, timeout=15)
    except:
        pass

def get_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://gamma-api.polymarket.com/markets?active=true&limit=1000"
    try:
        r = requests.get(url, headers=headers, timeout=30)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def monitor():
    global ciclo_count, VOL_START_1H, VOL_START_3H
    
    print("--- SCANNER 1H (TOP 30) & 3H (TOP 15) AVVIATO ---", flush=True)
    send_msg("✅ Bot Attivo\n- Report Orario: Top 30\n- Report 3 Ore: Top 15 (dati incrociati)")
    
    while True:
        markets = get_data()
        current_time = time.strftime('%H:%M')
        
        if markets:
            movers_1h = []
            movers_3h = []

            for m in markets:
                m_id = m.get('conditionId')
                if not m_id: continue
                
                vol_now = float(m.get('volume', 0))
                title = m.get('question', 'Unknown')
                slug = m.get('slug', '')
                link = f"https://polymarket.com/event/{slug}"

                # 1. Calcolo Orario (Top 30)
                if m_id in VOL_START_1H:
                    diff_1h = vol_now - VOL_START_1H[m_id]
                    if diff_1h > 0:
                        movers_1h.append({'title': title, 'diff': diff_1h, 'link': link})
                
                # 2. Calcolo 3 Ore (Top 15) - Incrocio dati storici
                if m_id in VOL_START_3H:
                    diff_3h = vol_now - VOL_START_3H[m_id]
                    if diff_3h > 0:
                        movers_3h.append({'title': title, 'diff': diff_3h, 'link': link})

                # Aggiornamento memorie per il prossimo giro
                VOL_START_1H[m_id] = vol_now
                if m_id not in VOL_START_3H:
                    VOL_START_3H[m_id] = vol_now

            # INVIO REPORT ORARIO
            if movers_1h:
                movers_1h.sort(key=lambda x: x['diff'], reverse=True)
                report = f"⏱️ *TOP 30 MOVEMENTS - ULTIMA ORA*\n🕒 {current_time}\n\n"
                for i, m in enumerate(movers_1h[:30], 1):
                    report += f"{i}. {m['title']}\n💰 +${m['diff']:,.0f}\n🔗 {m['link']}\n\n"
                    if len(report) > 3800:
                        send_msg(report)
                        report = ""
                if report: send_msg(report)

            # GESTIONE CICLO 3 ORE
            ciclo_count += 1
            if ciclo_count >= 3:
                if movers_3h:
                    movers_3h.sort(key=lambda x: x['diff'], reverse=True)
                    report_3h = f"🏆 *TOP 15 CUMULATIVA - ULTIME 3 ORE*\n🕒 {current_time}\n\n"
                    for i, m in enumerate(movers_3h[:15], 1):
                        report_3h += f"{i}. {m['title']}\n💰 +${m['diff']:,.0f}\n🔗 {m['link']}\n\n"
                    send_msg(report_3h)
                
                # Reset ciclo 3 ore: il volume attuale diventa la nuova base per le prossime 3 ore
                VOL_START_3H = VOL_START_1H.copy()
                ciclo_count = 0
            
            print(f"[{current_time}] Ciclo {ciclo_count}/3 completato. Mercati: {len(markets)}", flush=True)
        else:
            print(f"[{current_time}] Errore API: Dati non ricevuti.", flush=True)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor()
