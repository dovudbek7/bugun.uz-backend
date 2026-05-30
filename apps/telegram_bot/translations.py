import re

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
    """Convert Uzbek Latin to Cyrillic.
    Preserves: {placeholders}, <html tags>, /bot_commands.
    """
    parts = re.split(r'(\{[^}]*\}|<[^>]*>|/\w+)', text)
    result = []
    for part in parts:
        if (
            (part.startswith("{") and part.endswith("}"))
            or (part.startswith("<") and part.endswith(">"))
            or part.startswith("/")
        ):
            result.append(part)
        else:
            for lat, cyr in _MULTI_REPLACEMENTS:
                part = part.replace(lat, cyr)
            result.append("".join(_SINGLE_MAP.get(ch, ch) for ch in part))
    return "".join(result)


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
        "total_games_label": "Jami eventlar",
        "organizer_label": "Organizer",
        "region_label": "Viloyat",
        "phone_label": "Telefon",
        "yes": "✅ Ha",
        "no": "❌ Yo'q",
        "no_rating": "Reyting yo'q",
        "not_registered": "Avval /start bosing",
        "games_title": "📅 <b>Eventlaringiz</b>",
        "events_title": "📅 <b>Eventlaringiz</b>",
        "upcoming_label": "🟢 <b>Kelayotgan</b>",
        "completed_label": "✅ <b>Tugallangan</b>",
        "no_games": "Hali hech qanday eventga qo'shilmagansiz.\nEventlarni ko'rish uchun ilovani oching!",
        "location_prompt": "📍 Joylashuvingizni ulashing:",
        "location_button": "📍 Joylashuvni ulashish",
        "location_saved": "✅ Joylashuv saqlandi!\n\n📍 Lat: {lat:.4f}, Lon: {lon:.4f}",
        "help_text": (
            "🤖 <b>Community Events Bot</b>\n\n"
            "Mavjud buyruqlar:\n\n"
            "/start — Ro'yxatdan o'tish\n"
            "/profile — Profil va statistika\n"
            "/events — Qo'shilgan eventlarim\n"
            "/language — Tilni o'zgartirish\n"
            "/referral — Referal havola\n"
            "/help — Yordam\n\n"
            "<b>Nima qilish mumkin:</b>\n"
            "• Chess, mafia, board games va offline eventlarga qo'shilish\n"
            "• Event tarixini va reytingni kuzatish\n"
            "• Eventlar haqida bildirishnomalar olish"
        ),
        "event_joined": (
            "✅ Siz <b>{title}</b> eventiga qo'shildingiz!\n\n"
            "📅 Sana: {date}\n"
            "🕐 Vaqt: {time}\n"
            "📍 Joy: {location}\n"
            "📌 Manzil: {address}"
        ),
        "event_waiting": (
            "⏳ Siz <b>{title}</b> eventining kutish ro'yxatidasiz.\n\n"
            "📅 Sana: {date}\n"
            "🕐 Vaqt: {time}\n"
            "📍 Joy: {location}\n\n"
            "Bo'sh joy chiqsa avtomatik qo'shilasiz."
        ),
        "event_cancelled": (
            "❌ Siz <b>{title}</b> eventidan chiqib ketdingiz.\n\n"
            "📅 Sana: {date}\n"
            "🕐 Vaqt: {time}"
        ),
        "event_promoted": (
            "🎉 Tabriklaymiz! Kutish ro'yxatidan <b>{title}</b> eventiga qo'shildingiz!\n\n"
            "📅 Sana: {date}\n"
            "🕐 Vaqt: {time}\n"
            "📍 Joy: {location}\n"
            "📌 Manzil: {address}"
        ),
        "referral_link_msg": (
            "🔗 <b>Sizning referal havolangiz:</b>\n\n"
            "{link}\n\n"
            "👥 Siz orqali qo'shilganlar: <b>{count}</b> ta"
        ),
        "referral_joined": "🎉 <b>{name}</b> siz orqali platformaga qo'shildi!\n👥 Jami referallar: <b>{count}</b>",
        "open_event": "📱 Eventni ko'rish",
        "remind_me": "⏰ 30 daqiqa oldin eslatib tur",
        "reminder_set": "✅ Eslatma qo'yildi!",
        "reminder_too_late": "⚠️ Eventga 30 daqiqadan kam qoldi.",
        "event_reminder": (
            "⏰ <b>{title}</b> tez orada boshlanadi!\n\n"
            "🕐 Vaqt: {time}\n"
            "📍 Joy: {location}\n"
            "📌 Manzil: {address}"
        ),
        "event_org_cancelled": (
            "❌ <b>{title}</b> bekor qilindi.\n\n"
            "📅 Sana: {date}\n"
            "💬 Sabab: {reason}"
        ),
        "waiting_position_update": "⏳ <b>{title}</b> kutish ro'yxatida siz <b>{position}-o'rinda</b>siz.",
        "new_event_from_organizer": (
            "🆕 <b>{organizer}</b> yangi event ochdi!\n\n"
            "<b>{title}</b>\n"
            "📅 {date} | 🕐 {time}"
        ),
        "rate_organizer_prompt": (
            "🎮 <b>{title}</b> tugadi!\n"
            "Organizer <b>{organizer}</b> ni baholaysizmi?"
        ),
        "rate_organizer_done": "✅ Bahoingiz qabul qilindi!",
        "rate_organizer_skip": "⏭ O'tkazib yuborish",
        "already_rated": "✅ Siz allaqachon baholagansiz.",
        "subscribe_title": "📋 Kategoriyani tanlang:",
        "subscribed": "✅ <b>{category}</b> ga obuna bo'ldingiz.",
        "unsubscribed": "❎ <b>{category}</b> dan obuna bekor qilindi.",
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
        "total_games_label": "Всего мероприятий",
        "organizer_label": "Организатор",
        "region_label": "Регион",
        "phone_label": "Телефон",
        "yes": "✅ Да",
        "no": "❌ Нет",
        "no_rating": "Нет рейтинга",
        "not_registered": "Сначала отправьте /start",
        "games_title": "📅 <b>Ваши мероприятия</b>",
        "events_title": "📅 <b>Ваши мероприятия</b>",
        "upcoming_label": "🟢 <b>Предстоящие</b>",
        "completed_label": "✅ <b>Завершённые</b>",
        "no_games": "Вы ещё не записались ни на одно мероприятие.\nОткройте приложение для просмотра событий!",
        "location_prompt": "📍 Поделитесь местоположением:",
        "location_button": "📍 Поделиться локацией",
        "location_saved": "✅ Местоположение сохранено!\n\n📍 Lat: {lat:.4f}, Lon: {lon:.4f}",
        "help_text": (
            "🤖 <b>Community Events Bot</b>\n\n"
            "Доступные команды:\n\n"
            "/start — Регистрация\n"
            "/profile — Профиль и статистика\n"
            "/events — Мои мероприятия\n"
            "/language — Изменить язык\n"
            "/referral — Реферальная ссылка\n"
            "/help — Помощь\n\n"
            "<b>Возможности:</b>\n"
            "• Участие в офлайн мероприятиях (шахматы, мафия, настолки, встречи)\n"
            "• Отслеживание истории и рейтинга\n"
            "• Уведомления о мероприятиях"
        ),
        "event_joined": (
            "✅ Вы записались на <b>{title}</b>!\n\n"
            "📅 Дата: {date}\n"
            "🕐 Время: {time}\n"
            "📍 Место: {location}\n"
            "📌 Адрес: {address}"
        ),
        "event_waiting": (
            "⏳ Вы в списке ожидания для <b>{title}</b>.\n\n"
            "📅 Дата: {date}\n"
            "🕐 Время: {time}\n"
            "📍 Место: {location}\n\n"
            "Как только освободится место — вы автоматически попадёте в участники."
        ),
        "event_cancelled": (
            "❌ Вы отменили участие в <b>{title}</b>.\n\n"
            "📅 Дата: {date}\n"
            "🕐 Время: {time}"
        ),
        "event_promoted": (
            "🎉 Поздравляем! Вы попали в участники <b>{title}</b> из списка ожидания!\n\n"
            "📅 Дата: {date}\n"
            "🕐 Время: {time}\n"
            "📍 Место: {location}\n"
            "📌 Адрес: {address}"
        ),
        "referral_link_msg": (
            "🔗 <b>Ваша реферальная ссылка:</b>\n\n"
            "{link}\n\n"
            "👥 Приглашено через вас: <b>{count}</b>"
        ),
        "referral_joined": "🎉 <b>{name}</b> присоединился по вашей реферальной ссылке!\n👥 Всего рефералов: <b>{count}</b>",
        "open_event": "📱 Открыть мероприятие",
        "remind_me": "⏰ Напомнить за 30 минут",
        "reminder_set": "✅ Напоминание установлено!",
        "reminder_too_late": "⚠️ До мероприятия меньше 30 минут.",
        "event_reminder": (
            "⏰ <b>{title}</b> скоро начнётся!\n\n"
            "🕐 Время: {time}\n"
            "📍 Место: {location}\n"
            "📌 Адрес: {address}"
        ),
        "event_org_cancelled": (
            "❌ <b>{title}</b> отменено.\n\n"
            "📅 Дата: {date}\n"
            "💬 Причина: {reason}"
        ),
        "waiting_position_update": "⏳ В списке ожидания <b>{title}</b> вы на <b>{position} месте</b>.",
        "new_event_from_organizer": (
            "🆕 <b>{organizer}</b> открыл новое мероприятие!\n\n"
            "<b>{title}</b>\n"
            "📅 {date} | 🕐 {time}"
        ),
        "rate_organizer_prompt": (
            "🎮 <b>{title}</b> завершилось!\n"
            "Оцените организатора <b>{organizer}</b>?"
        ),
        "rate_organizer_done": "✅ Ваша оценка принята!",
        "rate_organizer_skip": "⏭ Пропустить",
        "already_rated": "✅ Вы уже оценили.",
        "subscribe_title": "📋 Выберите категорию:",
        "subscribed": "✅ Вы подписались на <b>{category}</b>.",
        "unsubscribed": "❎ Подписка на <b>{category}</b> отменена.",
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
        "total_games_label": "Total Events",
        "organizer_label": "Organizer",
        "region_label": "Region",
        "phone_label": "Phone",
        "yes": "✅ Yes",
        "no": "❌ No",
        "no_rating": "No rating yet",
        "not_registered": "Please send /start first",
        "games_title": "📅 <b>Your Events</b>",
        "events_title": "📅 <b>Your Events</b>",
        "upcoming_label": "🟢 <b>Upcoming</b>",
        "completed_label": "✅ <b>Completed</b>",
        "no_games": "You haven't joined any events yet.\nOpen the app to browse events!",
        "location_prompt": "📍 Please share your location:",
        "location_button": "📍 Share Location",
        "location_saved": "✅ Location saved!\n\n📍 Lat: {lat:.4f}, Lon: {lon:.4f}",
        "help_text": (
            "🤖 <b>Community Events Bot</b>\n\n"
            "Available commands:\n\n"
            "/start — Register\n"
            "/profile — Profile and stats\n"
            "/events — My events\n"
            "/language — Change language\n"
            "/referral — Referral link\n"
            "/help — Help\n\n"
            "<b>What you can do:</b>\n"
            "• Join offline events (chess, mafia, board games, meetups)\n"
            "• Track event history and rating\n"
            "• Get event notifications"
        ),
        "event_joined": (
            "✅ You joined <b>{title}</b>!\n\n"
            "📅 Date: {date}\n"
            "🕐 Time: {time}\n"
            "📍 Venue: {location}\n"
            "📌 Address: {address}"
        ),
        "event_waiting": (
            "⏳ You're on the waiting list for <b>{title}</b>.\n\n"
            "📅 Date: {date}\n"
            "🕐 Time: {time}\n"
            "📍 Venue: {location}\n\n"
            "You'll be automatically added when a spot opens up."
        ),
        "event_cancelled": (
            "❌ You cancelled your spot at <b>{title}</b>.\n\n"
            "📅 Date: {date}\n"
            "🕐 Time: {time}"
        ),
        "event_promoted": (
            "🎉 Great news! You've moved from the waiting list into <b>{title}</b>!\n\n"
            "📅 Date: {date}\n"
            "🕐 Time: {time}\n"
            "📍 Venue: {location}\n"
            "📌 Address: {address}"
        ),
        "referral_link_msg": (
            "🔗 <b>Your referral link:</b>\n\n"
            "{link}\n\n"
            "👥 Invited via you: <b>{count}</b>"
        ),
        "referral_joined": "🎉 <b>{name}</b> joined via your referral link!\n👥 Total referrals: <b>{count}</b>",
        "open_event": "📱 View Event",
        "remind_me": "⏰ Remind me 30 min before",
        "reminder_set": "✅ Reminder set!",
        "reminder_too_late": "⚠️ Less than 30 minutes until the event.",
        "event_reminder": (
            "⏰ <b>{title}</b> is starting soon!\n\n"
            "🕐 Time: {time}\n"
            "📍 Venue: {location}\n"
            "📌 Address: {address}"
        ),
        "event_org_cancelled": (
            "❌ <b>{title}</b> has been cancelled.\n\n"
            "📅 Date: {date}\n"
            "💬 Reason: {reason}"
        ),
        "waiting_position_update": "⏳ You are now <b>#{position}</b> in the waiting list for <b>{title}</b>.",
        "new_event_from_organizer": (
            "🆕 <b>{organizer}</b> posted a new event!\n\n"
            "<b>{title}</b>\n"
            "📅 {date} | 🕐 {time}"
        ),
        "rate_organizer_prompt": (
            "🎮 <b>{title}</b> is over!\n"
            "Would you rate organizer <b>{organizer}</b>?"
        ),
        "rate_organizer_done": "✅ Your rating has been submitted!",
        "rate_organizer_skip": "⏭ Skip",
        "already_rated": "✅ You already rated this organizer.",
        "subscribe_title": "📋 Choose a category:",
        "subscribed": "✅ Subscribed to <b>{category}</b>.",
        "unsubscribed": "❎ Unsubscribed from <b>{category}</b>.",
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
