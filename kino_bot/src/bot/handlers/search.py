"""
Smart Search handler (#4) — code, name, partial, multi-language.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import main_menu_kb, movies_list_kb, remove_kb
from src.core.config import settings
from src.core.security import sanitise_input
from src.db.base import AsyncSessionFactory
from src.db.repositories.movie_repo import MovieRepository
from src.db.repositories.user_repo import UserRepository
from src.services.cache import CacheService
from src.utils.i18n import t

router = Router(name="search")


class SearchFSM(StatesGroup):
    waiting_query = State()


# ── Entry points ──────────────────────────────────────────────────────────

@router.message(Command("search"))
@router.message(F.text.func(lambda x: x and x.startswith("🔍")))
async def cmd_search(message: Message, state: FSMContext, lang: str = "uz"):
    await state.set_state(SearchFSM.waiting_query)
    await message.answer(t("search_prompt", lang), reply_markup=remove_kb())


@router.callback_query(F.data == "search_again")
async def cb_search_again(callback: CallbackQuery, state: FSMContext, lang: str = "uz"):
    await state.set_state(SearchFSM.waiting_query)
    await callback.message.answer(t("search_prompt", lang), reply_markup=remove_kb())
    await callback.answer()


@router.message(Command("cancel"))
@router.message(F.text == "/cancel")
async def cmd_cancel(message: Message, state: FSMContext, lang: str = "uz"):
    await state.clear()
    await message.answer(t("search_cancelled", lang), reply_markup=main_menu_kb(lang))


# ── Query processing ──────────────────────────────────────────────────────

@router.message(SearchFSM.waiting_query)
async def process_search_query(message: Message, state: FSMContext, lang: str = "uz", user=None):
    raw = message.text or ""
    query = sanitise_input(raw.strip(), max_length=100)
    await state.clear()

    if len(query) < 2:
        await message.answer(t("search_too_short", lang), reply_markup=main_menu_kb(lang))
        return

    # Check cache
    cached = await CacheService.get_search(query, 0)
    if cached:
        movies_data, total = cached["movies"], cached["total"]
    else:
        async with AsyncSessionFactory() as session:
            movie_repo = MovieRepository(session)
            movies, total = await movie_repo.smart_search(query, page=0, per_page=settings.movies_per_page)
            movies_data = [_movie_to_dict(m) for m in movies]
        await CacheService.set_search(query, 0, {"movies": movies_data, "total": total})

    if not movies_data:
        await message.answer(t("search_no_results", lang, query=query), reply_markup=main_menu_kb(lang))
        return

    # Track search
    if user:
        async with AsyncSessionFactory() as session:
            user_repo = UserRepository(session)
            await user_repo.increment_searches(user.telegram_id)
            await session.commit()

    await state.update_data(last_query=query)

    text = t("search_results", lang, query=query, count=total)
    kb = movies_list_kb(
        movies=[_dict_to_pseudo(d) for d in movies_data],
        page=0,
        total=total,
        per_page=settings.movies_per_page,
        prefix=f"srch:{query}",
        lang=lang,
        include_search_again=True,
    )
    await message.answer(text, reply_markup=kb)


# ── Pagination for search results ─────────────────────────────────────────

@router.callback_query(F.data.startswith("srch:"))
async def cb_search_page(callback: CallbackQuery, lang: str = "uz"):
    parts = callback.data.split(":")
    # format: srch:<query>:<page>
    page = int(parts[-1])
    query = ":".join(parts[1:-1])

    cached = await CacheService.get_search(query, page)
    if cached:
        movies_data, total = cached["movies"], cached["total"]
    else:
        async with AsyncSessionFactory() as session:
            movie_repo = MovieRepository(session)
            movies, total = await movie_repo.smart_search(query, page=page, per_page=settings.movies_per_page)
            movies_data = [_movie_to_dict(m) for m in movies]
        await CacheService.set_search(query, page, {"movies": movies_data, "total": total})

    text = t("search_results", lang, query=query, count=total)
    kb = movies_list_kb(
        movies=[_dict_to_pseudo(d) for d in movies_data],
        page=page,
        total=total,
        per_page=settings.movies_per_page,
        prefix=f"srch:{query}",
        lang=lang,
        include_search_again=True,
    )
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# ── Inline query (share) ──────────────────────────────────────────────────

@router.inline_query()
async def inline_search(inline_query, lang: str = "uz"):
    from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
    query = inline_query.query.strip()
    if len(query) < 2:
        await inline_query.answer([], cache_time=1)
        return

    async with AsyncSessionFactory() as session:
        movie_repo = MovieRepository(session)
        movies, _ = await movie_repo.smart_search(query, page=0, per_page=10)

    results = []
    for movie in movies:
        results.append(InlineQueryResultArticle(
            id=str(movie.id),
            title=f"{movie.get_title(lang)} ({movie.year})",
            description=f"⭐ {movie.rating} | {', '.join(movie.genres or [])}",
            input_message_content=InputTextMessageContent(
                message_text=f"🎬 {movie.get_title(lang)} ({movie.year})\n"
                             f"🔑 Kod: <code>{movie.code}</code>\n"
                             f"⭐ Reyting: {movie.rating}/10",
                parse_mode="HTML",
            ),
            thumbnail_url=movie.poster_url,
        ))

    await inline_query.answer(results, cache_time=60)


# ── Helpers ───────────────────────────────────────────────────────────────

def _movie_to_dict(m) -> dict:
    return {
        "id": m.id, "code": m.code, "year": m.year, "rating": m.rating,
        "title": m.title, "title_uz": m.title_uz, "title_ru": m.title_ru,
        "title_en": m.title_en,
    }


class _dict_to_pseudo:
    """Thin wrapper to make a dict behave like a Movie for keyboards."""
    def __init__(self, d: dict):
        self.__dict__.update(d)

    def get_title(self, lang: str = "uz") -> str:
        mapping = {
            "uz": self.__dict__.get("title_uz") or self.__dict__.get("title_en") or self.__dict__.get("title", ""),
            "ru": self.__dict__.get("title_ru") or self.__dict__.get("title_en") or self.__dict__.get("title", ""),
            "en": self.__dict__.get("title_en") or self.__dict__.get("title", ""),
        }
        return mapping.get(lang, self.__dict__.get("title", ""))
