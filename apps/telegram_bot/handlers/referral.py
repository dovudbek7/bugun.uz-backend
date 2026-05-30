from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.telegram_bot.translations import t

router = Router()
User = get_user_model()


@sync_to_async
def _get_referral_data(tg_id):
    return (
        User.objects.filter(telegram_id=tg_id)
        .values("referral_code", "referral_count", "language")
        .first()
    )


@router.message(Command("referral"), StateFilter("*"))
async def referral_handler(message: Message):
    data = await _get_referral_data(message.from_user.id)
    if not data:
        await message.answer(t("not_registered", "uz_latn"))
        return

    lang = data["language"] or "uz_latn"
    bot_username = getattr(settings, "BOT_USERNAME", "")
    link = f"https://t.me/{bot_username}?start=ref_{data['referral_code']}"
    text = t("referral_link_msg", lang).format(link=link, count=data["referral_count"])
    await message.answer(text)
