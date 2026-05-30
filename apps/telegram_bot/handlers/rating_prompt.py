from aiogram import F, Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from apps.events.models import Event
from apps.ratings.models import Rating
from apps.telegram_bot.translations import t

router = Router()
User = get_user_model()


@sync_to_async
def _get_user(tg_id):
    return User.objects.filter(telegram_id=tg_id).first()


@sync_to_async
def _submit_rating(from_user, event_id, stars):
    event = Event.objects.select_related("organizer").filter(pk=event_id).first()
    if not event:
        return False, "not_found"
    if from_user.id == event.organizer_id:
        return False, "self"
    _, created = Rating.objects.get_or_create(
        from_user=from_user,
        to_user=event.organizer,
        event=event,
        defaults={"stars": stars},
    )
    if not created:
        return False, "already_rated"
    organizer = event.organizer
    received = Rating.objects.filter(to_user=organizer)
    if received.exists():
        organizer.rating = sum(r.stars for r in received) / received.count()
        organizer.save(update_fields=["rating", "updated_at"])
    return True, "ok"


@router.callback_query(F.data.startswith("rate_org:"))
async def rate_organizer_callback(callback: CallbackQuery):
    parts = callback.data.split(":")
    event_id = int(parts[1])
    stars = int(parts[2])

    user = await _get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    lang = user.language or "uz_latn"
    success, reason = await _submit_rating(user, event_id, stars)

    if reason == "already_rated":
        await callback.answer(t("already_rated", lang), show_alert=True)
    elif success:
        await callback.answer(t("rate_organizer_done", lang), show_alert=True)
        try:
            await callback.message.delete()
        except Exception:
            pass
    else:
        await callback.answer()


@router.callback_query(F.data.startswith("rate_org_skip:"))
async def rate_organizer_skip(callback: CallbackQuery):
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
