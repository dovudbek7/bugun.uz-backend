import logging

import requests
from django.conf import settings


logger = logging.getLogger(__name__)


def send_telegram_message(telegram_id, text):
    if not telegram_id:
        return False
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": telegram_id, "text": text}, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Telegram notification failed for user %s", telegram_id)
        return False
    return True
