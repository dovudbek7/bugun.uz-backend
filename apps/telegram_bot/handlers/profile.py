from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from apps.telegram_bot.translations import t
from apps.telegram_bot.utils import get_user_lang

router = Router()
User = get_user_model()


@sync_to_async
def _get_profile(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).first()


@router.message(Command("profile"))
async def profile_handler(message: Message):
    user = await _get_profile(message.from_user.id)
    if not user:
        await message.answer(t("not_registered", "uz_latn"))
        return

    lang = user.language or "uz_latn"

    name = user.full_name or user.telegram_username or "—"
    organizer = t("yes", lang) if user.is_organizer else t("no", lang)
    rating = f"{user.rating:.1f} ⭐" if user.rating else t("no_rating", lang)

    lines = [
        t("profile_title", lang),
        "",
        f"<b>{t('name', lang)}:</b> {name}",
        f"<b>{t('rating', lang)}:</b> {rating}",
        f"<b>{t('total_games', lang)}:</b> {user.total_attended}",
        f"<b>{t('organizer', lang)}:</b> {organizer}",
    ]
    if user.region:
        lines.append(f"<b>{t('region', lang)}:</b> {user.region}")
    if user.phone_number:
        lines.append(f"<b>{t('phone', lang)}:</b> {user.phone_number}")
    if user.show_telegram and user.telegram_username:
        lines.append(f"<b>Telegram:</b> @{user.telegram_username}")

    await message.answer("\n".join(lines))
