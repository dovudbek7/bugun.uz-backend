from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from apps.categories.models import Category, CategorySubscription
from apps.telegram_bot.translations import t

router = Router()
User = get_user_model()


@sync_to_async
def _get_user(tg_id):
    return User.objects.filter(telegram_id=tg_id).first()


@sync_to_async
def _get_categories():
    return list(Category.objects.all())


@sync_to_async
def _toggle_subscription(user, category_id):
    cat = Category.objects.filter(pk=category_id).first()
    if not cat:
        return None, False
    existing = CategorySubscription.objects.filter(user=user, category=cat).first()
    if existing:
        existing.delete()
        return cat, False
    CategorySubscription.objects.create(user=user, category=cat)
    return cat, True


@router.message(Command("subscribe"))
async def subscribe_handler(message: Message):
    user = await _get_user(message.from_user.id)
    if not user:
        await message.answer("Avval /start yuboring.")
        return
    lang = user.language or "uz_latn"
    categories = await _get_categories()
    buttons = [
        [InlineKeyboardButton(text=cat.get_title(lang), callback_data=f"sub:{cat.pk}")]
        for cat in categories
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(t("subscribe_title", lang), reply_markup=kb)


@router.callback_query(F.data.startswith("sub:"))
async def subscription_callback(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    user = await _get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return
    lang = user.language or "uz_latn"
    cat, subscribed = await _toggle_subscription(user, category_id)
    if not cat:
        await callback.answer()
        return
    cat_title = cat.get_title(lang)
    key = "subscribed" if subscribed else "unsubscribed"
    await callback.answer(t(key, lang).format(category=cat_title).replace("<b>", "").replace("</b>", ""), show_alert=True)
