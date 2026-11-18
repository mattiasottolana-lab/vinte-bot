import time
import json
import os
from datetime import datetime
from vinted_scraper import VintedScraper

TOKEN_1 = os.getenv("TELEGRAM_TOKEN")
TOKEN_2 = os.getenv("TELEGRAM_TOKEN_2")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHECK_INTERVAL = 40
SEEN_FILE = "seen_items.json"
MAX_PER_SEARCH = 5

SEARCHES = [
    {"name": "Nintendo Switch (Console)", "params": {"search_text": "Nintendo Switch", "catalog_ids": "3025", "order": "newest_first", "price_from": 2, "price_to": 80, "per_page": 10}},
    {"name": "Ralph Lauren", "params": {"search_text": "Ralph Lauren", "order": "newest_first", "price_from": 2, "price_to": 30, "per_page": 10}},
    {"name": "Nintendo 3DS", "params": {"search_text": "Nintendo 3DS", "catalog_ids": "3025", "order": "newest_first", "price_from": 2, "price_to": 70, "per_page": 10}},
    {"name": "Nintendo 3DS XL", "params": {"search_text": "3DS XL", "catalog_ids": "3025", "order": "newest_first", "price_from": 2, "price_to": 100, "per_page": 10}},
    {"name": "Giochi Nintendo Switch", "params": {"search_text": "Nintendo Switch", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 15, "per_page": 10}},
    {"name": "Giochi Nintendo 3DS", "params": {"search_text": "Nintendo 3DS", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 10, "per_page": 10}},
    {"name": "Giochi PlayStation", "params": {"search_text": "PlayStation", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 30, "per_page": 10}},
    {"name": "Giochi PlayStation 5", "params": {"search_text": "PlayStation 5", "catalog_ids": "3026", "order": "newest_first", "price_from": 2, "price_to": 30, "per_page": 10}},
    {"name": "Nike Mind 001", "params": {"search_text": "Nike Mind 001", "order": "newest_first", "price_from": 1, "price_to": 45, "per_page": 10}},
    {"name": "Carhartt", "params": {"search_text": "Carhartt", "order": "newest_first", "price_from": 1, "price_to": 30, "per_page": 10}},
    {"name": "Stone Island", "params": {"search_text": "Stone Island", "order": "newest_first", "price_from": 1, "price_to": 30, "per_page": 10}},
    {"name": "Ugg", "params": {"search_text": "Ugg", "order": "newest_first", "price_from": 1, "price_to": 30, "per_page": 10}},
    {"name": "Essentials", "params": {"search_text": "Essentials", "order": "newest_first", "price_from": 1, "price_to": 15, "per_page": 10}},
]

def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                data = json.load(f)
                return set(str(x) for x in data)
        except:
            return set()
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_with_token(token, title, price, item_id, search_name, url=None):
    import requests
    item_url = url if url and str(url).startswith("http") else f"https://www.vinted.it/items/{item_id}"
    
    message = (
        f"🔔 <b>Nuovo annuncio trovato!</b>\n\n"
        f"<b>{title}</b>\n\n"
        f"💰 <b>Prezzo:</b>
