from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
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


@sync_to_async
def _apply_referral(new_user_id: int, referral_code: str) -> "User | None":
    referrer = User.objects.filter(referral_code=referral_code).first()
    if not referrer:
        return None
    new_user = User.objects.filter(id=new_user_id).first()
    if not new_user or new_user.referred_by_id or new_user.id == referrer.id:
        return None
    new_user.referred_by = referrer
    new_user.save(update_fields=["referred_by"])
    User.objects.filter(id=referrer.id).update(referral_count=referrer.referral_count + 1)
    referrer.referral_count += 1
    return referrer


# ── Handlers ───────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def start_handler(message: Message, command: CommandObject, state: FSMContext):
    tg = message.from_user
    user, created = await _get_or_create_user(
        tg.id,
        tg.username or "",
        tg.full_name or "",
    )

    if command.args and command.args.startswith("event_"):
        event_id = command.args.replace("event_", "")
        lang = user.language or "uz_latn"
        mini_app_url = getattr(settings, "MINI_APP_URL", "").rstrip("/")
        if mini_app_url:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=t("open_event", lang),
                        web_app=WebAppInfo(url=f"{mini_app_url}/activity/{event_id}"),
                    )
                ]]
            )
            await message.answer(t("open_event", lang), reply_markup=kb)
        return

    ref_code = None
    if command.args and command.args.startswith("ref_"):
        ref_code = command.args[4:]

    if not created and user.phone_number:
        lang = user.language or "uz_latn"
        name = user.full_name or tg.full_name or tg.username or "friend"
        await message.answer(t("welcome_back", lang).format(name=name))
        mini_app_kb = _mini_app_keyboard(lang)
        if mini_app_kb:
            await message.answer(t("open_app", lang), reply_markup=mini_app_kb)
        return

    # Store referral code for use after registration completes
    await state.set_state(RegisterState.waiting_language)
    if ref_code:
        await state.update_data(ref_code=ref_code)
    await message.answer(
        t("choose_language", "uz_latn"),
        reply_markup=_language_keyboard(),
    )


@router.message(RegisterState.waiting_language, ~F.text.startswith("/"))
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
    ref_code = data.get("ref_code")

    avatar_url = await fetch_avatar_url(bot, message.from_user.id)
    await _save_phone_and_avatar(message.from_user.id, contact.phone_number, avatar_url)
    await state.clear()

    await message.answer(t("phone_saved", lang), reply_markup=ReplyKeyboardRemove())

    # Apply referral if present
    if ref_code:
        new_user = await _get_user(message.from_user.id)
        if new_user:
            referrer = await _apply_referral(new_user.id, ref_code)
            if referrer and referrer.telegram_id:
                referrer_lang = referrer.language or "uz_latn"
                new_name = new_user.full_name or message.from_user.full_name or message.from_user.username or "Someone"
                notif_text = t("referral_joined", referrer_lang).format(
                    name=new_name, count=referrer.referral_count
                )
                await bot.send_message(referrer.telegram_id, notif_text)

    mini_app_kb = _mini_app_keyboard(lang)
    if mini_app_kb:
        await message.answer(t("open_app", lang), reply_markup=mini_app_kb)


@router.message(RegisterState.waiting_phone, ~F.text.startswith("/"))
async def waiting_phone_fallback(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz_latn")
    await message.answer(t("phone_request", lang), reply_markup=_phone_keyboard(lang))


# ── /language command ──────────────────────────────────────────────────────────

def _language_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek (Lotin)", callback_data="lang:uz_latn"),
            InlineKeyboardButton(text="🇺🇿 Ўзбек (Кирил)", callback_data="lang:uz_cyrl"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ],
    ])


@router.message(Command("language"), StateFilter("*"))
async def language_command(message: Message):
    await message.answer(t("choose_language", "uz_latn"), reply_markup=_language_inline_keyboard())


@router.callback_query(F.data.startswith("lang:"), StateFilter("*"))
async def language_callback(callback: CallbackQuery):
    lang = callback.data.split(":", 1)[1]
    valid = {"uz_latn", "uz_cyrl", "ru", "en"}
    if lang not in valid:
        await callback.answer()
        return

    await _save_language(callback.from_user.id, lang)

    lang_names = {
        "uz_latn": "🇺🇿 O'zbek (Lotin)",
        "uz_cyrl": "🇺🇿 Ўзбек (Кирил)",
        "ru": "🇷🇺 Русский",
        "en": "🇬🇧 English",
    }
    saved_text = t("language_saved", lang)
    await callback.answer(saved_text, show_alert=False)
    await callback.message.edit_text(
        f"{saved_text}\n\n{lang_names[lang]}"
    )
