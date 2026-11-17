import requests
import time
import json
import os
import re
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9297766331:AAGk6Mw54p0HKlJ7MAJfwZB10rH2y1Qj0yg")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "8284365011")

CHECK_INTERVAL = 40
SEEN_FILE = "seen_items.json"

SEARCHES = [
    {"name": "Nintendo Switch (Console)", "url": "https://www.vinted.it/catalog?search_text=Nintendo+Switch&catalog[]=3025&order=price_low_to_high&price_from=1&price_to=80"},
    {"name": "Ralph Lauren", "url": "https://www.vinted.it/catalog?search_text=Ralph+Lauren&order=price_low_to_high&price_from=1&price_to=30"},
    {"name": "Nintendo 3DS", "url": "https://www.vinted.it/catalog?search_text=Nintendo+3DS&catalog[]=3025&order=price_low_to_high&price_from=1&price_to=70"},
    {"name": "Nintendo 3DS XL", "url": "https://www.vinted.it/catalog?search_text=3DS+XL&catalog[]=3025&order=price_low_to_high&price_from=1&price_to=100"},
    {"name": "Giochi Nintendo Switch", "url": "https://www.vinted.it/catalog?search_text=Nintendo+Switch&catalog[]=3026&order=price_low_to_high&price_from=1&price_to=15"},
    {"name": "Giochi Nintendo 3DS", "url": "https://www.vinted.it/catalog?search_text=Nintendo+3DS&catalog[]=3026&order=price_low_to_high&price_from=1&price_to=10"},
    {"name": "Giochi PlayStation", "url": "https://www.vinted.it/catalog?search_text=PlayStation&catalog[]=3026&order=price_low_to_high&price_from=1&price_to=30"},
    {"name": "Giochi PlayStation 5", "url": "https://www.vinted.it/catalog?search_text=PlayStation+5&catalog[]=3026&order=price_low_to_high&price_from=1&price_to=30"},
]

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Referer": "https://www.vinted.it/",
})

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                return set(json.load(f))
        except:
            return set()
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_to_telegram(title, price, item_id, search_name):
    item_url = f"https://www.vinted.it/items/{item_id}"
    message = (
        f"🔔 <b>Nuovo annuncio trovato!</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"💰 <b>Prezzo:</b> {price} €\n"
        f"📁 <b>Ricerca:</b> {search_name}\n"
        f"🆔 <b>ID:</b> {item_id}\n\n"
        f"🛒 <b><a href='{item_url}'>COMPRA SUBITO</a></b>\n"
        f"🔗 {item_url}"
    )

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": False}

    try:
        r = requests.post(api_url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OK {search_name} | {price}€ | {title[:40]}")
        else:
            print(f"Errore Telegram: {r.status_code}")
    except Exception as e:
        print("Errore invio Telegram:", e)

def extract_items(html):
    items = []
    # Metodo più robusto per estrarre gli annunci
    pattern = r'"id":(\d+).*?"title":"(.*?)".*?"price":\{"amount":"([\d.]+)"'
    matches = re.findall(pattern, html, re.DOTALL)
    for match in matches[:15]:  # limita ai primi 15 per evitare troppi
        item_id, title, price = match
        try:
            items.append({"id": int(item_id), "title": title, "price": price})
        except:
            continue
    return items

def check_search(search, seen):
    name = search["name"]
    url = search["url"]
    try:
        response = session.get(url, timeout=15)
        if response.status_code != 200:
            print(f"[{name}] Errore HTTP {response.status_code}")
            return

        items = extract_items(response.text)
        print(f"[{name}] Trovati {len(items)} annunci nella pagina")
        new_count = 0

        for item in items:
            item_id = item["id"]
            if item_id not in seen:
                seen.add(item_id)
                send_to_telegram(item["title"], item["price"], item_id, name)
                new_count += 1

        if new_count > 0:
            save_seen(seen)
            print(f"[{name}] Inviati {new_count} nuovi")
        else:
            print(f"[{name}] Nessun nuovo")

    except Exception as e:
        print(f"[{name}] Errore: {e}")

def main():
    seen = load_seen()
    print("Bot Vinted avviato (modalità pagina migliorata)")
    print(f"Ricerche: {len(SEARCHES)}")
    print(f"Controllo ogni {CHECK_INTERVAL} secondi")

    for search in SEARCHES:
        check_search(search, seen)
    save_seen(seen)
    print(f"ID caricati: {len(seen)}")
    print("In ascolto...")

    while True:
        time.sleep(CHECK_INTERVAL)
        for search in SEARCHES:
            check_search(search, seen)
            time.sleep(2)

if __name__ == "__main__":
    main()
