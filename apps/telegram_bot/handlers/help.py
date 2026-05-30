from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message

from apps.telegram_bot.translations import t
from apps.telegram_bot.utils import get_user_lang

router = Router()


@router.message(Command("help"), StateFilter("*"))
async def help_handler(message: Message):
    lang = await get_user_lang(message.from_user.id)
    await message.answer(t("help_text", lang))
