"""
Favorites & Watch History handlers (#8, #9).
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import favorites_kb, history_kb, main_menu_kb
from src.core.config import settings
from src.db.base import AsyncSessionFactory
from src.db.repositories.favorite_repo import FavoriteRepository
from src.db.repositories.history_repo import HistoryRepository
from src.utils.i18n import t

router = Router(name="favorites")


# ── FAVORITES (#8) ─────────────────────────────────────────────────────────

@router.message(Command("favorites"))
@router.message(F.text.func(lambda x: x and x.startswith("❤️")))
async def cmd_favorites(message: Message, lang: str = "uz", user=None):
    if not user:
        await message.answer(t("error_generic", lang))
        return
    await _show_favorites(message, 0, lang, user.id)


@router.callback_query(F.data.startswith("favpage:"))
async def cb_favorites_page(callback: CallbackQuery, lang: str = "uz", user=None):
    if not user:
        await callback.answer()
        return
    page = int(callback.data.split(":")[1])
    await _show_favorites(callback.message, page, lang, user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("fav:add:"))
async def cb_fav_add(callback: CallbackQuery, lang: str = "uz", user=None):
    if not user:
        await callback.answer(t("error_generic", lang), show_alert=True)
        return
    movie_id = int(callback.data.split(":")[2])
    async with AsyncSessionFactory() as session:
        fav_repo = FavoriteRepository(session)
        _, created = await fav_repo.add(user.id, movie_id)
        await session.commit()

    if created:
        await callback.answer(t("favorite_added", lang), show_alert=True)
    else:
        await callback.answer(t("favorite_already", lang), show_alert=True)


@router.callback_query(F.data.startswith("fav:remove:"))
async def cb_fav_remove(callback: CallbackQuery, lang: str = "uz", user=None):
    if not user:
        await callback.answer(t("error_generic", lang), show_alert=True)
        return
    movie_id = int(callback.data.split(":")[2])
    async with AsyncSessionFactory() as session:
        fav_repo = FavoriteRepository(session)
        removed = await fav_repo.remove(user.id, movie_id)
        await session.commit()

    if removed:
        await callback.answer(t("favorite_removed", lang), show_alert=True)
    else:
        await callback.answer("ℹ️", show_alert=False)


async def _show_favorites(
    message: Message, page: int, lang: str, user_id: int, edit: bool = False
) -> None:
    async with AsyncSessionFactory() as session:
        fav_repo = FavoriteRepository(session)
        movies, total = await fav_repo.get_user_favorites(user_id, page=page)

    if not movies and page == 0:
        text = t("favorites_empty", lang)
        kb = main_menu_kb(lang)
        if edit:
            await message.answer(text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)
        return

    text = t("favorites_header", lang, count=total)
    kb = favorites_kb(movies, page, total, settings.movies_per_page, lang)
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


# ── WATCH HISTORY (#9) ─────────────────────────────────────────────────────

@router.message(Command("history"))
@router.message(F.text.func(lambda x: x and x.startswith("📜")))
async def cmd_history(message: Message, lang: str = "uz", user=None):
    if not user:
        await message.answer(t("error_generic", lang))
        return
    await _show_history(message, 0, lang, user.id)


@router.callback_query(F.data.startswith("histpage:"))
async def cb_history_page(callback: CallbackQuery, lang: str = "uz", user=None):
    if not user:
        await callback.answer()
        return
    page = int(callback.data.split(":")[1])
    await _show_history(callback.message, page, lang, user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data == "history:clear")
async def cb_history_clear(callback: CallbackQuery, lang: str = "uz", user=None):
    if not user:
        await callback.answer()
        return
    async with AsyncSessionFactory() as session:
        hist_repo = HistoryRepository(session)
        count = await hist_repo.clear_user_history(user.id)
        await session.commit()
    await callback.answer(f"🗑 {count} ta o'chirildi", show_alert=True)
    await callback.message.answer(t("history_empty", lang), reply_markup=main_menu_kb(lang))


async def _show_history(
    message: Message, page: int, lang: str, user_id: int, edit: bool = False
) -> None:
    async with AsyncSessionFactory() as session:
        hist_repo = HistoryRepository(session)
        movies, total = await hist_repo.get_user_history(user_id, page=page)

    if not movies and page == 0:
        await message.answer(t("history_empty", lang), reply_markup=main_menu_kb(lang))
        return

    text = t("history_header", lang, count=total)
    kb = history_kb(movies, page, total, settings.movies_per_page, lang)
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)
