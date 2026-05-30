import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def send_telegram_message(telegram_id, text, parse_mode="HTML", reply_markup=None):
    if not telegram_id:
        return False
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    payload = {"chat_id": telegram_id, "text": text, "parse_mode": parse_mode}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Telegram notification failed for user %s", telegram_id)
        return False
    return True


def send_telegram_venue(telegram_id, latitude, longitude, title, address):
    if not telegram_id:
        return False
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendVenue"
    try:
        response = requests.post(
            url,
            json={
                "chat_id": telegram_id,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "title": title,
                "address": address,
            },
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Telegram venue send failed for user %s", telegram_id)
        return False
    return True
