from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Contact,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.telegram_bot.translations import LANG_BUTTON_MAP, TEXTS, t
from apps.telegram_bot.utils import fetch_avatar_url

router = Router()
User = get_user_model()


class RegisterState(StatesGroup):
    waiting_language = State()
    waiting_phone = State()


# ── Keyboards ──────────────────────────────────────────────────────────────────

def _language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek (Lotin)"), KeyboardButton(text="🇺🇿 Ўзбек (Кирил)")],
            [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _phone_keyboard(lang: str):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("phone_button", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def _mini_app_keyboard(lang: str):
    url = getattr(settings, "MINI_APP_URL", "")
    if not url or url in ("https://t.me", ""):
        return None
    try:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=t("open_app", lang), web_app=WebAppInfo(url=url))]]
        )
        return kb
    except Exception:
        return None


# ── DB helpers ─────────────────────────────────────────────────────────────────

@sync_to_async
def _get_or_create_user(tg_id: int, username: str, full_name: str):
    user, created = User.objects.get_or_create(
        telegram_id=tg_id,
        defaults={
            "username": f"tg_{tg_id}",
            "telegram_username": username,
            "full_name": full_name,
        },
    )
    if not created and username and user.telegram_username != username:
        user.telegram_username = username
        user.save(update_fields=["telegram_username", "updated_at"])
    return user, created


@sync_to_async
def _save_language(tg_id: int, lang: str):
    User.objects.filter(telegram_id=tg_id).update(language=lang)


@sync_to_async
def _save_phone_and_avatar(tg_id: int, phone: str, avatar: str):
    fields = {"phone_number": phone}
    if avatar:
        fields["avatar"] = avatar
    User.objects.filter(telegram_id=tg_id).update(**fields)


@sync_to_async
def _get_user(tg_id: int):
    return User.objects.filter(telegram_id=tg_id).first()


# ── Handlers ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    tg = message.from_user
    user, created = await _get_or_create_user(
        tg.id,
        tg.username or "",
        tg.full_name or "",
    )

    if not created and user.phone_number:
        # Returning user — greet in their language
        lang = user.language or "uz_latn"
        name = user.full_name or tg.full_name or tg.username or "friend"
        await message.answer(t("welcome_back", lang).format(name=name))
        return

    # New user (or existing without phone) — start registration
    await state.set_state(RegisterState.waiting_language)
    await message.answer(
        t("choose_language", "uz_latn"),
        reply_markup=_language_keyboard(),
    )


@router.message(RegisterState.waiting_language)
async def language_selected(message: Message, state: FSMContext):
    lang = LANG_BUTTON_MAP.get(message.text)
    if not lang:
        await message.answer(t("choose_language", "uz_latn"), reply_markup=_language_keyboard())
        return

    await _save_language(message.from_user.id, lang)
    await state.update_data(lang=lang)
    await state.set_state(RegisterState.waiting_phone)

    name = message.from_user.full_name or message.from_user.username or "friend"
    await message.answer(
        f"{t('welcome_new', lang).format(name=name)}\n\n{t('phone_request', lang)}",
        reply_markup=_phone_keyboard(lang),
    )


@router.message(RegisterState.waiting_phone, F.contact)
async def contact_handler(message: Message, state: FSMContext, bot):
    contact: Contact = message.contact
    if contact.user_id != message.from_user.id:
        data = await state.get_data()
        lang = data.get("lang", "uz_latn")
        await message.answer(t("phone_request", lang), reply_markup=_phone_keyboard(lang))
        return

    data = await state.get_data()
    lang = data.get("lang", "uz_latn")

    avatar_url = await fetch_avatar_url(bot, message.from_user.id)
    await _save_phone_and_avatar(message.from_user.id, contact.phone_number, avatar_url)
    await state.clear()

    await message.answer(t("phone_saved", lang), reply_markup=ReplyKeyboardRemove())

    mini_app_kb = _mini_app_keyboard(lang)
    if mini_app_kb:
        await message.answer(t("open_app", lang), reply_markup=mini_app_kb)


@router.message(RegisterState.waiting_phone)
async def waiting_phone_fallback(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz_latn")
    await message.answer(t("phone_request", lang), reply_markup=_phone_keyboard(lang))
