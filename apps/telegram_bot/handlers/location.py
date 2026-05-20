from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from apps.telegram_bot.translations import t
from apps.telegram_bot.utils import get_user_lang

router = Router()
User = get_user_model()


def _location_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("location_button", lang), request_location=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


@sync_to_async
def _save_location(telegram_id, lat, lon):
    User.objects.filter(telegram_id=telegram_id).update(
        last_latitude=lat,
        last_longitude=lon,
    )


@router.message(Command("location"))
async def location_command(message: Message):
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("location_prompt", lang), reply_markup=_location_keyboard(lang))


@router.message(F.location)
async def location_received(message: Message):
    lang = await get_user_lang(message.from_user.id)
    loc = message.location
    await _save_location(message.from_user.id, loc.latitude, loc.longitude)
    await message.answer(
        t("location_saved", lang).format(lat=loc.latitude, lon=loc.longitude),
        reply_markup=ReplyKeyboardRemove(),
    )
