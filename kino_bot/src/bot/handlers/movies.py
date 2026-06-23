"""
Movie detail, catalog, filter, top, recent handlers (#4–#8).
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import (
    country_list_kb, filter_menu_kb, genres_kb, language_list_kb,
    main_menu_kb, movie_detail_kb, movies_list_kb, rating_kb,
    top_count_kb, top_movies_kb, top_period_kb,
)
from src.core.config import settings
from src.db.base import AsyncSessionFactory
from src.db.repositories.favorite_repo import FavoriteRepository
from src.db.repositories.history_repo import HistoryRepository
from src.db.repositories.movie_repo import MovieRepository
from src.db.repositories.user_repo import UserRepository
from src.services.cache import CacheService
from src.utils.formatters import format_movie_card
from src.utils.i18n import t

router = Router(name="movies")


class FilterFSM(StatesGroup):
    waiting_year = State()


# ── CATALOG ────────────────────────────────────────────────────────────────

@router.message(Command("catalog"))
@router.message(F.text.func(lambda x: x and x.startswith("🎬")))
async def cmd_catalog(message: Message, lang: str = "uz"):
    async with AsyncSessionFactory() as session:
        repo = MovieRepository(session)
        movies, total = await repo.get_all(page=0)

    kb = movies_list_kb(movies, 0, total, settings.movies_per_page, "catalog", lang)
    await message.answer(f"📋 <b>Filmlar katalogi</b> — {total} ta kino", reply_markup=kb)


@router.callback_query(F.data.startswith("catalog:"))
async def cb_catalog_page(callback: CallbackQuery, lang: str = "uz"):
    page = int(callback.data.split(":")[1])
    async with AsyncSessionFactory() as session:
        repo = MovieRepository(session)
        movies, total = await repo.get_all(page=page)
    kb = movies_list_kb(movies, page, total, settings.movies_per_page, "catalog", lang)
    await callback.message.edit_text(f"📋 <b>Filmlar katalogi</b> — {total} ta kino", reply_markup=kb)
    await callback.answer()


# ── MOVIE DETAIL ───────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("movie:"))
async def cb_movie_detail(callback: CallbackQuery, lang: str = "uz", user=None):
    movie_id = int(callback.data.split(":")[1])

    # Try cache
    cached = await CacheService.get_movie(movie_id)
    if cached:
        text = cached["card"]
        is_fav = False
    else:
        async with AsyncSessionFactory() as session:
            repo = MovieRepository(session)
            movie = await repo.get_by_id(movie_id)
            if not movie:
                await callback.answer(t("movie_not_found", lang), show_alert=True)
                return
            await repo.increment_view(movie_id)
            await session.commit()
            text = format_movie_card(movie, lang)
            await CacheService.set_movie(movie_id, {"card": text})

    is_fav = False
    if user:
        async with AsyncSessionFactory() as session:
            fav_repo = FavoriteRepository(session)
            is_fav = await fav_repo.is_favorite(user.id, movie_id)
            # Add to watch history
            hist_repo = HistoryRepository(session)
            await hist_repo.add(user.id, movie_id)
            user_repo = UserRepository(session)
            await user_repo.increment_views(user.telegram_id)
            await session.commit()

    async with AsyncSessionFactory() as session:
        repo = MovieRepository(session)
        movie = await repo.get_by_id(movie_id)

    if not movie:
        await callback.answer(t("movie_not_found", lang), show_alert=True)
        return

    kb = movie_detail_kb(movie, is_fav, lang)
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


# ── FILTER SEARCH (#5) ─────────────────────────────────────────────────────

@router.message(Command("filter"))
@router.message(F.text.func(lambda x: x and x.startswith("🎛")))
async def cmd_filter(message: Message, lang: str = "uz"):
    await message.answer("🎛 <b>Filtrlash</b>", reply_markup=filter_menu_kb(lang))


@router.callback_query(F.data == "filter_menu")
async def cb_filter_menu(callback: CallbackQuery, lang: str = "uz"):
    await callback.message.edit_text("🎛 <b>Filtrlash</b>", reply_markup=filter_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "filter:genre")
async def cb_filter_genre(callback: CallbackQuery, lang: str = "uz"):
    async with AsyncSessionFactory() as session:
        genres = await MovieRepository(session).get_all_genres()
    await callback.message.edit_text(
        t("filter_choose_genre", lang), reply_markup=genres_kb(genres, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("filter_genre:"))
async def cb_filter_genre_result(callback: CallbackQuery, lang: str = "uz"):
    genre = callback.data.split(":", 1)[1]
    await _show_filter_results(callback, lang, genre=genre)


@router.callback_query(F.data == "filter:year")
async def cb_filter_year(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.set_state(FilterFSM.waiting_year)
    await callback.message.answer(t("filter_choose_year", lang))
    await callback.answer()


@router.message(FilterFSM.waiting_year)
async def process_filter_year(message: Message, state: FSMContext, lang: str = "uz"):
    await state.clear()
    raw = message.text.strip()
    year_from = year_to = None
    try:
        if "-" in raw:
            parts = raw.split("-")
            year_from = int(parts[0].strip())
            year_to = int(parts[1].strip())
        else:
            year_from = year_to = int(raw)
    except ValueError:
        await message.answer("❌ Noto'g'ri format. Misol: 2020 yoki 2010-2020")
        return
    await _show_filter_results_msg(message, lang, year_from=year_from, year_to=year_to)


@router.callback_query(F.data == "filter:country")
async def cb_filter_country(callback: CallbackQuery, lang: str = "uz"):
    async with AsyncSessionFactory() as session:
        countries = await MovieRepository(session).get_distinct_countries()
    await callback.message.edit_text(
        t("filter_choose_country", lang), reply_markup=country_list_kb(countries, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("filter_country:"))
async def cb_filter_country_result(callback: CallbackQuery, lang: str = "uz"):
    country = callback.data.split(":", 1)[1]
    await _show_filter_results(callback, lang, country=country)


@router.callback_query(F.data == "filter:language")
async def cb_filter_language(callback: CallbackQuery, lang: str = "uz"):
    async with AsyncSessionFactory() as session:
        languages = await MovieRepository(session).get_distinct_languages()
    await callback.message.edit_text(
        t("filter_choose_language", lang), reply_markup=language_list_kb(languages, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("filter_language:"))
async def cb_filter_language_result(callback: CallbackQuery, lang: str = "uz"):
    language = callback.data.split(":", 1)[1]
    await _show_filter_results(callback, lang, language=language)


@router.callback_query(F.data == "filter:rating")
async def cb_filter_rating(callback: CallbackQuery, lang: str = "uz"):
    await callback.message.edit_text(t("filter_choose_rating", lang), reply_markup=rating_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("filter_rating:"))
async def cb_filter_rating_result(callback: CallbackQuery, lang: str = "uz"):
    rating = float(callback.data.split(":")[1])
    await _show_filter_results(callback, lang, min_rating=rating)


# ── TOP MOVIES (#6) ────────────────────────────────────────────────────────

@router.message(Command("top"))
@router.message(F.text.func(lambda x: x and x.startswith("⭐")))
async def cmd_top(message: Message, lang: str = "uz"):
    await message.answer(t("top_choose_period", lang), reply_markup=top_period_kb(lang))


@router.callback_query(F.data == "top_menu")
async def cb_top_menu(callback: CallbackQuery, lang: str = "uz"):
    await callback.message.edit_text(t("top_choose_period", lang), reply_markup=top_period_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("top:"))
async def cb_top_period(callback: CallbackQuery, lang: str = "uz"):
    period = callback.data.split(":")[1]
    await callback.message.edit_text(
        t("top_choose_count", lang), reply_markup=top_count_kb(period, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("top_count:"))
async def cb_top_count(callback: CallbackQuery, lang: str = "uz"):
    _, period, count_str = callback.data.split(":")
    limit = int(count_str)

    cached = await CacheService.get_top(period, limit)
    if cached:
        movies_data = cached
    else:
        async with AsyncSessionFactory() as session:
            movies = await MovieRepository(session).get_top_movies(period=period, limit=limit)
            movies_data = [
                {"id": m.id, "code": m.code, "year": m.year, "rating": m.rating,
                 "title": m.title, "title_uz": m.title_uz, "title_ru": m.title_ru, "title_en": m.title_en}
                for m in movies
            ]
        await CacheService.set_top(period, limit, movies_data)

    period_label = t(f"period_{period}", lang) if period != "alltime" else t("period_alltime", lang)
    text = t("top_header", lang, count=limit, period=period_label)
    for i, m in enumerate(movies_data, 1):
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        medal = medals.get(i, f"{i}.")
        title = m.get("title_uz") or m.get("title_en") or m.get("title", "")
        if lang == "ru":
            title = m.get("title_ru") or m.get("title_en") or m.get("title", "")
        elif lang == "en":
            title = m.get("title_en") or m.get("title", "")
        text += f"{medal} {title} — ⭐{m['rating']}\n"

    from src.bot.handlers.search import _dict_to_pseudo
    kb = top_movies_kb([_dict_to_pseudo(m) for m in movies_data], period, lang)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# ── RECENT MOVIES (#7) ─────────────────────────────────────────────────────

@router.message(Command("recent"))
@router.message(F.text.func(lambda x: x and x.startswith("🆕")))
async def cmd_recent(message: Message, lang: str = "uz"):
    await _show_recent(message, 0, lang)


@router.callback_query(F.data.startswith("recent:"))
async def cb_recent_page(callback: CallbackQuery, lang: str = "uz"):
    page = int(callback.data.split(":")[1])
    await _show_recent(callback.message, page, lang, edit=True)
    await callback.answer()


# ── SETTINGS ───────────────────────────────────────────────────────────────

@router.message(Command("settings"))
@router.message(F.text.func(lambda x: x and x.startswith("⚙️")))
async def cmd_settings(message: Message, lang: str = "uz"):
    from src.bot.keyboards import settings_kb
    from src.utils.i18n import lang_name
    await message.answer(
        t("settings_header", lang, lang=lang_name(lang)),
        reply_markup=settings_kb(lang),
    )


@router.callback_query(F.data == "settings:change_lang")
async def cb_change_lang(callback: CallbackQuery):
    from src.bot.keyboards import language_kb
    await callback.message.edit_text(t("choose_language", "uz"), reply_markup=language_kb())
    await callback.answer()


# ── ABOUT ──────────────────────────────────────────────────────────────────

@router.message(F.text.func(lambda x: x and x.startswith("ℹ️")))
async def cmd_about(message: Message, lang: str = "uz"):
    async with AsyncSessionFactory() as session:
        movie_count = await MovieRepository(session).count_total()
        user_count = await UserRepository(session).count_total()
    await message.answer(
        t("about", lang, movies=movie_count, users=user_count),
        reply_markup=main_menu_kb(lang),
    )


# ── PRIVATE HELPERS ────────────────────────────────────────────────────────

async def _show_filter_results(
    callback: CallbackQuery,
    lang: str,
    genre=None, country=None, language=None,
    min_rating=None, year_from=None, year_to=None,
    page: int = 0,
) -> None:
    async with AsyncSessionFactory() as session:
        movies, total = await MovieRepository(session).filter_movies(
            genre=genre, country=country, language=language,
            min_rating=min_rating, year_from=year_from, year_to=year_to,
            page=page,
        )
    if not movies:
        await callback.answer(t("filter_no_results", lang), show_alert=True)
        return
    kb = movies_list_kb(movies, page, total, settings.movies_per_page, "catalog", lang)
    text = t("filter_results", lang, count=total)
    await callback.message.edit_text(text, reply_markup=kb)


async def _show_filter_results_msg(
    message: Message, lang: str,
    genre=None, country=None, language=None,
    min_rating=None, year_from=None, year_to=None,
) -> None:
    async with AsyncSessionFactory() as session:
        movies, total = await MovieRepository(session).filter_movies(
            genre=genre, country=country, language=language,
            min_rating=min_rating, year_from=year_from, year_to=year_to,
        )
    if not movies:
        await message.answer(t("filter_no_results", lang), reply_markup=main_menu_kb(lang))
        return
    kb = movies_list_kb(movies, 0, total, settings.movies_per_page, "catalog", lang)
    await message.answer(t("filter_results", lang, count=total), reply_markup=kb)


async def _show_recent(message: Message, page: int, lang: str, edit: bool = False) -> None:
    async with AsyncSessionFactory() as session:
        movies, total = await MovieRepository(session).get_recent(page=page)
    kb = movies_list_kb(movies, page, total, settings.movies_per_page, "recent", lang)
    text = t("recent_header", lang)
    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)
