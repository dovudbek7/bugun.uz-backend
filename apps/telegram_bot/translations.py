# ── Uzbek Latin → Cyrillic transliteration ────────────────────────────────────

_MULTI_REPLACEMENTS = [
    # Multi-char first (order matters)
    ("O'", "Ў"), ("o'", "ў"),
    ("Oʻ", "Ў"), ("oʻ", "ў"),
    ("G'", "Ғ"), ("g'", "ғ"),
    ("Gʻ", "Ғ"), ("gʻ", "ғ"),
    ("Sh", "Ш"), ("sh", "ш"),
    ("Ch", "Ч"), ("ch", "ч"),
    ("Ng", "Нг"), ("ng", "нг"),
    ("Ts", "Тс"), ("ts", "тс"),
    ("Yo", "Ё"), ("yo", "ё"),
    ("Yu", "Ю"), ("yu", "ю"),
    ("Ya", "Я"), ("ya", "я"),
    ("Je", "Е"), ("je", "е"),
]

_SINGLE_MAP = {
    'A': 'А', 'B': 'Б', 'D': 'Д', 'E': 'Э', 'F': 'Ф',
    'G': 'Г', 'H': 'Ҳ', 'I': 'И', 'J': 'Ж', 'K': 'К',
    'L': 'Л', 'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П',
    'Q': 'Қ', 'R': 'Р', 'S': 'С', 'T': 'Т', 'U': 'У',
    'V': 'В', 'X': 'Х', 'Y': 'Й', 'Z': 'З',
    'a': 'а', 'b': 'б', 'd': 'д', 'e': 'э', 'f': 'ф',
    'g': 'г', 'h': 'ҳ', 'i': 'и', 'j': 'ж', 'k': 'к',
    'l': 'л', 'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п',
    'q': 'қ', 'r': 'р', 's': 'с', 't': 'т', 'u': 'у',
    'v': 'в', 'x': 'х', 'y': 'й', 'z': 'з',
}


def latin_to_cyrillic(text: str) -> str:
    """Convert Uzbek Latin script to Cyrillic."""
    for lat, cyr in _MULTI_REPLACEMENTS:
        text = text.replace(lat, cyr)
    return "".join(_SINGLE_MAP.get(ch, ch) for ch in text)


# ── Texts (uz_latn + ru + en only; uz_cyrl is auto-generated) ─────────────────

TEXTS = {
    "uz_latn": {
        "choose_language": "🌐 Tilni tanlang:",
        "btn_uz_latn": "🇺🇿 O'zbek (Lotin)",
        "btn_uz_cyrl": "🇺🇿 O'zbek (Kiril)",
        "btn_ru": "🇷🇺 Ruscha",
        "btn_en": "🇬🇧 Inglizcha",
        "language_saved": "✅ Til saqlandi!",
        "phone_request": "📱 Telefon raqamingizni ulashing:",
        "phone_button": "📱 Raqamni ulashish",
        "phone_saved": "✅ Raqam saqlandi! Ro'yxatdan o'tish tugallandi.",
        "welcome_new": "Salom, <b>{name}</b>! 👋\n\nOffline community events platformasiga xush kelibsiz.",
        "welcome_back": "Qaytib keldingiz, <b>{name}</b>! 👋",
        "open_app": "🎮 Ilovani ochish",
        "profile_title": "👤 <b>Profil</b>",
        "name_label": "Ism",
        "rating_label": "Reyting",
        "total_games_label": "Jami o'yinlar",
        "organizer_label": "Organizer",
        "region_label": "Viloyat",
        "phone_label": "Telefon",
        "yes": "✅ Ha",
        "no": "❌ Yo'q",
        "no_rating": "Reyting yo'q",
        "not_registered": "Avval /start bosing",
        "games_title": "🎮 <b>O'yinlaringiz</b>",
        "upcoming_label": "🟢 <b>Kelayotgan</b>",
        "completed_label": "✅ <b>Tugatilgan</b>",
        "no_games": "Hali hech qanday eventga qo'shilmagansiz.\nEventlarni ko'rish uchun ilovani oching!",
        "location_prompt": "📍 Joylashuvingizni ulashing:",
        "location_button": "📍 Joylashuvni ulashish",
        "location_saved": "✅ Joylashuv saqlandi!\n\n📍 Lat: {lat:.4f}, Lon: {lon:.4f}",
        "help_text": (
            "🤖 <b>Community Events Bot</b>\n\n"
            "Mavjud buyruqlar:\n\n"
            "/start — Ro'yxatdan o'tish va sozlash\n"
            "/profile — Profil va statistika\n"
            "/games — Qo'shilgan eventlar\n"
            "/location — Joylashuvni ulashish\n"
            "/help — Yordam\n\n"
            "<b>Nima qilish mumkin:</b>\n"
            "• Chess, mafia, board games va boshqa offline eventlarga qo'shilish\n"
            "• O'yin tarixini va reytingni kuzatish\n"
            "• Eventlar haqida bildirishnomalar olish"
        ),
    },
    "ru": {
        "choose_language": "🌐 Выберите язык:",
        "btn_uz_latn": "🇺🇿 Узбекский (латиница)",
        "btn_uz_cyrl": "🇺🇿 Узбекский (кириллица)",
        "btn_ru": "🇷🇺 Русский",
        "btn_en": "🇬🇧 Английский",
        "language_saved": "✅ Язык сохранён!",
        "phone_request": "📱 Поделитесь номером телефона:",
        "phone_button": "📱 Поделиться номером",
        "phone_saved": "✅ Номер сохранён! Регистрация завершена.",
        "welcome_new": "Привет, <b>{name}</b>! 👋\n\nДобро пожаловать на платформу офлайн мероприятий.",
        "welcome_back": "С возвращением, <b>{name}</b>! 👋",
        "open_app": "🎮 Открыть приложение",
        "profile_title": "👤 <b>Профиль</b>",
        "name_label": "Имя",
        "rating_label": "Рейтинг",
        "total_games_label": "Всего игр",
        "organizer_label": "Организатор",
        "region_label": "Регион",
        "phone_label": "Телефон",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "no_rating": "Нет рейтинга",
        "not_registered": "Сначала отправьте /start",
        "games_title": "🎮 <b>Ваши игры</b>",
        "upcoming_label": "🟢 <b>Предстоящие</b>",
        "completed_label": "✅ <b>Завершённые</b>",
        "no_games": "Вы ещё не записались ни на один event.\nОткройте приложение для просмотра событий!",
        "location_prompt": "📍 Поделитесь местоположением:",
        "location_button": "📍 Поделиться локацией",
        "location_saved": "✅ Местоположение сохранено!\n\n📍 Lat: {lat:.4f}, Lon: {lon:.4f}",
        "help_text": (
            "🤖 <b>Community Events Bot</b>\n\n"
            "Доступные команды:\n\n"
            "/start — Регистрация и настройка\n"
            "/profile — Профиль и статистика\n"
            "/games — Записанные мероприятия\n"
            "/location — Поделиться локацией\n"
            "/help — Помощь\n\n"
            "<b>Возможности:</b>\n"
            "• Участие в офлайн мероприятиях (шахматы, мафия, настолки, встречи)\n"
            "• Отслеживание истории игр и рейтинга\n"
            "• Уведомления о мероприятиях"
        ),
    },
    "en": {
        "choose_language": "🌐 Choose your language:",
        "btn_uz_latn": "🇺🇿 Uzbek (Latin)",
        "btn_uz_cyrl": "🇺🇿 Uzbek (Cyrillic)",
        "btn_ru": "🇷🇺 Russian",
        "btn_en": "🇬🇧 English",
        "language_saved": "✅ Language saved!",
        "phone_request": "📱 Please share your phone number:",
        "phone_button": "📱 Share Phone Number",
        "phone_saved": "✅ Phone saved! Registration complete.",
        "welcome_new": "Hello, <b>{name}</b>! 👋\n\nWelcome to the offline community events platform.",
        "welcome_back": "Welcome back, <b>{name}</b>! 👋",
        "open_app": "🎮 Open Mini App",
        "profile_title": "👤 <b>Profile</b>",
        "name_label": "Name",
        "rating_label": "Rating",
        "total_games_label": "Total Games",
        "organizer_label": "Organizer",
        "region_label": "Region",
        "phone_label": "Phone",
        "yes": "✅ Yes",
        "no": "❌ No",
        "no_rating": "No rating yet",
        "not_registered": "Please send /start first",
        "games_title": "🎮 <b>Your Games</b>",
        "upcoming_label": "🟢 <b>Upcoming</b>",
        "completed_label": "✅ <b>Completed</b>",
        "no_games": "You haven't joined any events yet.\nOpen the app to browse events!",
        "location_prompt": "📍 Please share your location:",
        "location_button": "📍 Share Location",
        "location_saved": "✅ Location saved!\n\n📍 Lat: {lat:.4f}, Lon: {lon:.4f}",
        "help_text": (
            "🤖 <b>Community Events Bot</b>\n\n"
            "Available commands:\n\n"
            "/start — Register and set up account\n"
            "/profile — View profile and stats\n"
            "/games — See your joined events\n"
            "/location — Share your location\n"
            "/help — Show this help\n\n"
            "<b>What you can do:</b>\n"
            "• Join offline events (chess, mafia, board games, meetups)\n"
            "• Track game history and rating\n"
            "• Get event notifications"
        ),
    },
}

LANG_BUTTON_MAP = {
    "🇺🇿 O'zbek (Lotin)": "uz_latn",
    "🇺🇿 O'zbek (Kiril)": "uz_cyrl",
    "🇷🇺 Ruscha": "ru",
    "🇷🇺 Русский": "ru",
    "🇬🇧 Inglizcha": "en",
    "🇬🇧 English": "en",
}


def t(key: str, lang: str = "uz_latn") -> str:
    """Return translated text. uz_cyrl is auto-converted from uz_latn."""
    if lang == "uz_cyrl":
        source = TEXTS["uz_latn"].get(key, key)
        return latin_to_cyrillic(source)
    lang_texts = TEXTS.get(lang, TEXTS["uz_latn"])
    return lang_texts.get(key, TEXTS["uz_latn"].get(key, key))
