"""
Start handler — language selection on first run (#12).
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import language_kb, main_menu_kb, settings_kb
from src.db.base import AsyncSessionFactory
from src.db.repositories.user_repo import UserRepository
from src.utils.i18n import t

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, user=None, lang: str = "uz", is_new_user: bool = False):
    """On first visit: show language picker. On return: show main menu."""
    if is_new_user or (user and not user.language):
        await message.answer(t("choose_language", "uz"), reply_markup=language_kb())
    else:
        await message.answer(
            t("welcome", lang, name=message.from_user.first_name or ""),
            reply_markup=main_menu_kb(lang),
        )


@router.callback_query(F.data.startswith("lang:"))
async def cb_set_language(callback: CallbackQuery, user=None):
    lang = callback.data.split(":")[1]
    if lang not in ("uz", "ru", "en"):
        await callback.answer("Invalid language")
        return

    async with AsyncSessionFactory() as session:
        user_repo = UserRepository(session)
        await user_repo.set_language(callback.from_user.id, lang)
        await session.commit()

    await callback.message.edit_text(t("language_set", lang))
    await callback.message.answer(
        t("welcome", lang, name=callback.from_user.first_name or ""),
        reply_markup=main_menu_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "home")
async def cb_home(callback: CallbackQuery, lang: str = "uz"):
    await callback.message.answer(
        "🏠 Bosh menyu / Main menu",
        reply_markup=main_menu_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str = "uz"):
    text = (
        "📖 <b>Buyruqlar / Commands:</b>\n\n"
        "/start — Botni qayta ishga tushirish\n"
        "/search — Film qidirish\n"
        "/top — Top kinolar\n"
        "/recent — Yangi kinolar\n"
        "/favorites — Sevimlilar\n"
        "/history — Ko'rish tarixi\n"
        "/settings — Sozlamalar\n"
        "/help — Yordam\n"
    )
    await message.answer(text, reply_markup=main_menu_kb(lang))


# Channel subscription check
@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: CallbackQuery, user=None, lang: str = "uz"):
    from aiogram.exceptions import TelegramBadRequest
    from src.core.config import settings
    if not settings.enable_channel_guard or not settings.required_channel:
        await callback.answer("✅ OK")
        return
    try:
        member = await callback.bot.get_chat_member(
            settings.required_channel, callback.from_user.id
        )
        if member.status in ("member", "administrator", "creator"):
            async with AsyncSessionFactory() as session:
                ur = UserRepository(session)
                await session.execute(
                    __import__("sqlalchemy").update(
                        __import__("src.db.models.user", fromlist=["User"]).User
                    )
                    .where(__import__("src.db.models.user", fromlist=["User"]).User.telegram_id == callback.from_user.id)
                    .values(is_subscribed=True)
                )
                await session.commit()
            await callback.answer("✅ " + t("language_set", lang))
            await callback.message.answer(
                t("welcome", lang, name=callback.from_user.first_name or ""),
                reply_markup=main_menu_kb(lang),
            )
        else:
            await callback.answer(t("not_subscribed", lang), show_alert=True)
    except Exception:
        await callback.answer(t("not_subscribed", lang), show_alert=True)
