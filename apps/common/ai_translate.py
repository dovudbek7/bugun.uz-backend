"""AI translation helper backed by OpenAI.

Translates free-form text into the three canonical languages used across the
project: Uzbek Latin (uz_latn), Russian (ru) and English (en). Uzbek Cyrillic
(uz_cyrl) is never produced here — it is generated on the fly from uz_latn via
``apps.telegram_bot.translations.latin_to_cyrillic``.
"""
import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_client = None

# Minimum characters worth sending to the API. Shorter strings (or empty ones)
# are skipped to avoid wasting requests.
MIN_LENGTH = 2

_SYSTEM_PROMPT = (
    "You are a translation engine for an events platform. "
    "Detect the source language of the user's text and translate it into three "
    "languages: Uzbek (Latin script), Russian, and English. "
    "Preserve the original formatting, line breaks, emojis and punctuation. "
    "Do not add commentary, notes or quotes. "
    "Return ONLY a JSON object with exactly these keys: "
    '"uz_latn", "ru", "en".'
)


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI

        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY (CHATGPT_API_KEY) is not configured.")
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def translate_text(text: str) -> dict:
    """Translate ``text`` into uz_latn / ru / en.

    Returns a dict ``{"uz_latn": ..., "ru": ..., "en": ...}``. Returns an empty
    dict for blank/too-short input. Raises on API/parse failure so callers can
    mark the record as failed and retry.
    """
    text = (text or "").strip()
    if len(text) < MIN_LENGTH:
        return {}

    client = _get_client()
    response = client.chat.completions.create(
        model=settings.OPENAI_TRANSLATE_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    raw = response.choices[0].message.content
    data = json.loads(raw)

    result = {key: (data.get(key) or "").strip() for key in ("uz_latn", "ru", "en")}
    if not any(result.values()):
        raise ValueError(f"Translation returned no content: {raw!r}")
    return result
