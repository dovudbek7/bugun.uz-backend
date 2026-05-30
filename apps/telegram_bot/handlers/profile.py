import html

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from apps.telegram_bot.translations import t

router = Router()
User = get_user_model()


@sync_to_async
def _get_profile(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).first()


@router.message(Command("profile"), StateFilter("*"))
async def profile_handler(message: Message):
    user = await _get_profile(message.from_user.id)
    if not user:
        await message.answer(t("not_registered", "uz_latn"))
        return

    lang = user.language or "uz_latn"
    name = html.escape(user.full_name or user.telegram_username or "—")
    rating_str = f"⭐ {user.rating:.1f}" if user.rating else t("no_rating", lang)
    organizer_icon = "✅" if user.is_organizer else "❌"

    lines = [f"👤 <b>{name}</b>"]
    if user.telegram_username:
        lines.append(f"@{html.escape(user.telegram_username)}")
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append(f"⭐ <b>{t('rating_label', lang)}:</b> {rating_str}")
    lines.append(f"🎮 <b>{t('total_games_label', lang)}:</b> {user.total_attended}")
    lines.append(f"🏅 <b>{t('organizer_label', lang)}:</b> {organizer_icon}")
    if user.region:
        lines.append(f"📍 <b>{t('region_label', lang)}:</b> {html.escape(user.region)}")
    if user.phone_number:
        lines.append(f"📱 <b>{t('phone_label', lang)}:</b> {html.escape(user.phone_number)}")

    await message.answer("\n".join(lines))
