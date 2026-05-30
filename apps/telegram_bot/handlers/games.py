import html

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.telegram_bot.translations import t

router = Router()
User = get_user_model()


@sync_to_async
def _get_user_games(telegram_id):
    try:
        user = User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None, "uz_latn", [], []

    from apps.attendance.models import Attendance
    from apps.events.models import Event

    attendances = (
        Attendance.objects.filter(user=user, event__status=Event.STATUS_UPCOMING)
        .select_related("event")
        .exclude(status=Attendance.STATUS_CANCELLED)
        .order_by("event__event_date", "event__event_time")
    )

    upcoming = [
        (att.event.id, att.event.title,
         att.event.event_date.strftime("%d.%m.%Y"),
         att.event.event_time.strftime("%H:%M"))
        for att in attendances
    ]

    return user, user.language or "uz_latn", upcoming, []


def _event_keyboard(events, lang):
    """Inline keyboard: one button per upcoming event → opens webapp detail page."""
    mini_app_url = getattr(settings, "MINI_APP_URL", "").rstrip("/")
    if not mini_app_url:
        return None
    rows = []
    for event_id, title, date_str, time_str in events[:5]:
        url = f"{mini_app_url}/activity/{event_id}"
        label = f"📍 {title[:28]}" if len(title) > 28 else f"📍 {title}"
        try:
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=url))])
        except Exception:
            pass
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


@router.message(Command("events", "games"), StateFilter("*"))
async def games_handler(message: Message):
    user, lang, upcoming, completed = await _get_user_games(message.from_user.id)

    if not user:
        await message.answer(t("not_registered", "uz_latn"))
        return

    lines = [t("events_title", lang), ""]

    if upcoming:
        for _, title, date_str, time_str in upcoming[:10]:
            lines.append(f"• <b>{html.escape(title)}</b> — {date_str}, {time_str}")
    else:
        lines.append(t("no_games", lang))

    kb = _event_keyboard(upcoming, lang) if upcoming else None
    await message.answer("\n".join(lines), reply_markup=kb)
