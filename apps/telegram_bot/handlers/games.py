from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async
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
        Attendance.objects.filter(user=user)
        .select_related("event")
        .exclude(status=Attendance.STATUS_CANCELLED)
        .order_by("-event__event_date")
    )

    upcoming = []
    completed = []
    for att in attendances:
        event = att.event
        entry = f"• {event.title} — {event.event_date}"
        if event.status == Event.STATUS_UPCOMING:
            upcoming.append(entry)
        else:
            completed.append(entry)

    return user, user.language or "uz_latn", upcoming, completed


@router.message(Command("games"))
async def games_handler(message: Message):
    user, lang, upcoming, completed = await _get_user_games(message.from_user.id)

    if not user:
        await message.answer(t("not_registered", "uz_latn"))
        return

    lines = [t("games_title", lang), ""]

    if upcoming:
        lines.append(t("upcoming_label", lang))
        lines.extend(upcoming[:5])
        lines.append("")

    if completed:
        lines.append(t("completed_label", lang))
        lines.extend(completed[:5])
        lines.append("")

    if not upcoming and not completed:
        lines.append(t("no_games", lang))

    await message.answer("\n".join(lines))
