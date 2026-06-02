from datetime import timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.attendance.models import EventReminder
from apps.events.models import Event
from apps.telegram_bot.translations import t

router = Router()
User = get_user_model()


@router.callback_query(F.data.startswith("remind:"))
async def remind_callback(callback: CallbackQuery):
    event_id = int(callback.data.split(":")[1])
    tg_id = callback.from_user.id

    user = await sync_to_async(User.objects.filter(telegram_id=tg_id).first)()
    if not user:
        await callback.answer()
        return

    lang = user.language or "uz_latn"

    event = await sync_to_async(Event.objects.filter(pk=event_id).first)()
    if not event:
        await callback.answer()
        return

    now = timezone.now()
    if event.starts_at <= now:
        await callback.answer(t("event_already_ended", lang), show_alert=True)
        return

    remind_at = event.starts_at - timedelta(minutes=30)
    if remind_at <= now:
        await callback.answer(t("reminder_too_late", lang), show_alert=True)
        return

    await sync_to_async(EventReminder.objects.update_or_create)(
        user=user,
        event=event,
        defaults={"remind_at": remind_at, "sent": False},
    )
    await callback.answer(t("reminder_set", lang), show_alert=False)
