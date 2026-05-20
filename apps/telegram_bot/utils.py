import logging

from aiogram import Bot
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


@sync_to_async
def get_user_lang(telegram_id: int) -> str:
    try:
        return User.objects.filter(telegram_id=telegram_id).values_list("language", flat=True).get()
    except User.DoesNotExist:
        return "uz_latn"


async def fetch_avatar_url(bot: Bot, user_id: int) -> str:
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            file = await bot.get_file(file_id)
            token = bot.token
            return f"https://api.telegram.org/file/bot{token}/{file.file_path}"
    except Exception:
        logger.debug("Could not fetch avatar for user %s", user_id)
    return ""
