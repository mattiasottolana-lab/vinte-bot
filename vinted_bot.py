import time
import json
import os
from datetime import datetime
from vinted_scraper import VintedScraper

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHECK_INTERVAL = 60
SEEN_FILE = "seen_items.json"

SEARCHES = [
    {"name": "Nintendo Switch (Console)", "params": {"search_text": "Nintendo Switch", "catalog_ids": "3025", "order": "newest_first", "price_from": 2, "price_to": 80, "per_page": 20}},
    {"name": "Ralph Lauren", "params": {"search_text": "Ralph Lauren", "order": "newest_first", "price_from": 2, "price_to": 30, "per_page": 20}},
    {"name": "Nintendo 3DS", "params": {"search_text": "Nintendo 3DS", "catalog_ids": "3025", "order": "newest_first", "price_from": 2, "price_to": 70, "per_page": 20}},
    {"name": "Nintendo 3DS XL", "params": {"search_text": "3DS XL", "catalog_ids": "3025", "order": "newest_first", "price_from": 2, "price_to": 100, "per_page": 20}},
    {"name": "Giochi Nintendo Switch", "params": {"search_text": "Nintendo Switch", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 15, "per_page": 20}},
    {"name": "Giochi Nintendo 3DS", "params": {"search_text": "Nintendo 3DS", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 10, "per_page": 20}},
    {"name": "Giochi PlayStation", "params": {"search_text": "PlayStation", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 30, "per_page": 20}},
    {"name": "Giochi PlayStation 5", "params": {"search_text": "PlayStation 5", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 30, "per_page": 20}},
]

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

def send_to_telegram(title, price, item_id, search_name, url=None):
    import requests
    item_url = url if url and str(url).startswith("http") else f"https://www.vinted.it/items/{item_id}"
    
    message = (
        f"🔔 <b>Nuovo annuncio trovato!</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"💰 <b>Prezzo:</b> {price} €\n"
        f"📁 <b>Ricerca:</b> {search_name}\n"
        f"🆔 <b>ID:</b> {item_id}\n\n"
        f"🛒 <a href=\"{item_url}\"><b>COMPRA SUBITO</b></a>\n"
        f"🔗 <a href=\"{item_url}\">{item_url}</a>"
    )

    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    try:
        r = requests.post(api_url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OK {search_name} | {price}€ | {title[:40]}")
        elif r.status_code == 429:
            print("Limite Telegram, attendo 10 secondi...")
            time.sleep(10)
        else:
            print(f"Errore Telegram: {r.status_code}")
    except Exception as e:
        print("Errore invio Telegram:", e)
    
    time.sleep(2)  # un annuncio ogni 2 secondi

def get_price(item):
    try:
        if hasattr(item, "price") and item.price:
            if hasattr(item.price, "amount"):
                return item.price.amount
            elif isinstance(item.price, (int, float, str)):
                return item.price
        if hasattr(item, "total_item_price") and item.total_item_price:
            return item.total_item_price
    except:
        pass
    return "?"

def check_search(scraper, search, seen):
    name = search["name"]
    params = search["params"]
    try:
        items = scraper.search(params)
        print(f"[{name}] Trovati {len(items)} annunci")
        new_count = 0

        for item in items:
            item_id = getattr(item, "id", None)
            if not item_id or item_id in seen:
                continue
            seen.add(item_id)
            price = get_price(item)
            url = getattr(item, "url", None) or getattr(item, "path", None)
            send_to_telegram(item.title, price, item_id, name, url)
            new_count += 1

        if new_count > 0:
            save_seen(seen)
            print(f"[{name}] Inviati {new_count} nuovi")
        else:
            print(f"[{name}] Nessun nuovo")

    except Exception as e:
        print(f"[{name}] Errore: {e}")

def main():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERRORE: TELEGRAM_TOKEN o TELEGRAM_CHAT_ID mancanti!")
        return

    seen = load_seen()
    scraper = VintedScraper("https://www.vinted.it")
    print("Bot Vinted avviato (messaggi ogni 2 secondi)")
    print(f"Ricerche: {len(SEARCHES)}")
    print(f"Controllo ogni {CHECK_INTERVAL} secondi")

    for search in SEARCHES:
        check_search(scraper, search, seen)
    save_seen(seen)
    print(f"ID caricati: {len(seen)}")
    print("In ascolto...")

    while True:
        time.sleep(CHECK_INTERVAL)
        for search in SEARCHES:
            check_search(scraper, search, seen)
            time.sleep(1)

if __name__ == "__main__":
    main()
