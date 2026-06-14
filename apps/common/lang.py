"""Resolve the request language for localized API responses.

Language codes match ``accounts.User.language``: uz_latn, uz_cyrl, ru, en.
Priority: Accept-Language header → ?lang= query param → authenticated user's
saved language → default uz_latn.
"""

DEFAULT_LANG = "uz_latn"
SUPPORTED = {"uz_latn", "uz_cyrl", "ru", "en"}

# Normalize loose client values (e.g. "uz", "uz-Cyrl", "EN") to internal codes.
_ALIASES = {
    "uz": "uz_latn",
    "uz-latn": "uz_latn",
    "uz_latn": "uz_latn",
    "uz-cyrl": "uz_cyrl",
    "uz_cyrl": "uz_cyrl",
    "ru": "ru",
    "ru-ru": "ru",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
}


def normalize_lang(value):
    if not value:
        return None
    # Accept-Language may carry quality values: "ru,en;q=0.8" → take first token.
    token = value.split(",")[0].split(";")[0].strip().lower()
    if token in _ALIASES:
        return _ALIASES[token]
    if token in SUPPORTED:
        return token
    return None


def get_request_language(request) -> str:
    if request is None:
        return DEFAULT_LANG

    header = normalize_lang(request.META.get("HTTP_ACCEPT_LANGUAGE"))
    if header:
        return header

    query = normalize_lang(request.query_params.get("lang")) if hasattr(request, "query_params") else None
    if query:
        return query

    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False) and getattr(user, "language", None):
        return user.language

    return DEFAULT_LANG
