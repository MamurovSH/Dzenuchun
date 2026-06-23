"""
All bot keyboards — ReplyKeyboard + InlineKeyboard.
Fully multi-language and supports inline navigation (#12, #13).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from src.core.config import settings
from src.utils.i18n import t


# ── Language Selection (#12) ───────────────────────────────────────────────

def language_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇷🇺 Русский",   callback_data="lang:ru"),
            InlineKeyboardButton(text="🇺🇸 English",   callback_data="lang:en"),
        ]
    ])


# ── Main Menu ──────────────────────────────────────────────────────────────

def main_menu_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn_catalog", lang)), KeyboardButton(text=t("btn_search", lang))],
            [KeyboardButton(text=t("btn_filter", lang)),  KeyboardButton(text=t("btn_top", lang))],
            [KeyboardButton(text=t("btn_recent", lang)),  KeyboardButton(text=t("btn_favorites", lang))],
            [KeyboardButton(text=t("btn_history", lang)), KeyboardButton(text=t("btn_settings", lang))],
            [KeyboardButton(text=t("btn_about", lang))],
        ],
        resize_keyboard=True,
    )


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ── Pagination helper ──────────────────────────────────────────────────────

def pagination_row(
    page: int,
    total: int,
    per_page: int,
    prefix: str,
    lang: str = "uz",
) -> List[InlineKeyboardButton]:
    """Returns a row of Prev / Page / Next buttons."""
    total_pages = max(1, (total + per_page - 1) // per_page)
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(text=t("btn_prev", lang), callback_data=f"{prefix}:{page - 1}"))
    row.append(InlineKeyboardButton(
        text=f"📄 {page + 1}/{total_pages}",
        callback_data="noop",
    ))
    if (page + 1) * per_page < total:
        row.append(InlineKeyboardButton(text=t("btn_next", lang), callback_data=f"{prefix}:{page + 1}"))
    return row


def home_row(lang: str = "uz", include_search_again: bool = False) -> List[InlineKeyboardButton]:
    row = []
    if include_search_again:
        row.append(InlineKeyboardButton(text=t("btn_search_again", lang), callback_data="search_again"))
    row.append(InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"))
    return row


# ── Movie List (Catalog / Search / Filter / Recent) ────────────────────────

def movies_list_kb(
    movies: list,
    page: int,
    total: int,
    per_page: int,
    prefix: str,
    lang: str = "uz",
    include_search_again: bool = False,
) -> InlineKeyboardMarkup:
    buttons = []
    for movie in movies:
        title = movie.get_title(lang) if hasattr(movie, "get_title") else str(movie)
        year = getattr(movie, "year", "")
        rating = getattr(movie, "rating", "")
        movie_id = getattr(movie, "id", 0)
        buttons.append([
            InlineKeyboardButton(
                text=f"🎬 {title} ({year}) ⭐{rating}",
                callback_data=f"movie:{movie_id}",
            )
        ])

    nav = pagination_row(page, total, per_page, prefix, lang)
    if nav:
        buttons.append(nav)

    buttons.append(home_row(lang, include_search_again))
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Movie Detail ───────────────────────────────────────────────────────────

def movie_detail_kb(
    movie,
    is_favorite: bool = False,
    lang: str = "uz",
) -> InlineKeyboardMarkup:
    movie_id = getattr(movie, "id", 0)
    fav_text = t("btn_fav_remove", lang) if is_favorite else t("btn_fav_add", lang)
    fav_data = f"fav:remove:{movie_id}" if is_favorite else f"fav:add:{movie_id}"

    buttons = []

    # Watch + Trailer
    watch_url = getattr(movie, "watch_url", None)
    trailer_url = getattr(movie, "trailer_url", None)
    url_row = []
    if watch_url:
        url_row.append(InlineKeyboardButton(text=t("btn_watch", lang), url=watch_url))
    if trailer_url:
        url_row.append(InlineKeyboardButton(text=t("btn_trailer", lang), url=trailer_url))
    if url_row:
        buttons.append(url_row)

    # Favorite + Share
    buttons.append([
        InlineKeyboardButton(text=fav_text, callback_data=fav_data),
        InlineKeyboardButton(
            text=t("btn_share", lang),
            switch_inline_query=f"{getattr(movie, 'code', '')}",
        ),
    ])

    # Navigation
    buttons.append([
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="catalog:0"),
        InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Top Movies (#6) ────────────────────────────────────────────────────────

def top_period_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"📅 {t('period_weekly', lang)}",  callback_data="top:weekly"),
            InlineKeyboardButton(text=f"📆 {t('period_monthly', lang)}", callback_data="top:monthly"),
        ],
        [
            InlineKeyboardButton(text=f"🗓 {t('period_yearly', lang)}",  callback_data="top:yearly"),
            InlineKeyboardButton(text=f"🏆 {t('period_alltime', lang)}", callback_data="top:alltime"),
        ],
        home_row(lang),
    ])


def top_count_kb(period: str, lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Top 10",  callback_data=f"top_count:{period}:10"),
            InlineKeyboardButton(text="Top 50",  callback_data=f"top_count:{period}:50"),
            InlineKeyboardButton(text="Top 100", callback_data=f"top_count:{period}:100"),
        ],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="top_menu")],
        home_row(lang),
    ])


def top_movies_kb(movies: list, period: str, lang: str = "uz") -> InlineKeyboardMarkup:
    medals = ["🥇", "🥈", "🥉"]
    buttons = []
    for i, movie in enumerate(movies):
        medal = medals[i] if i < 3 else f"{i + 1}."
        title = movie.get_title(lang) if hasattr(movie, "get_title") else str(movie)
        rating = getattr(movie, "rating", "")
        movie_id = getattr(movie, "id", 0)
        buttons.append([InlineKeyboardButton(
            text=f"{medal} {title} ⭐{rating}",
            callback_data=f"movie:{movie_id}",
        )])
    buttons.append([
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="top_menu"),
        InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Filter (#5) ────────────────────────────────────────────────────────────

def filter_menu_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Janr / Genre",       callback_data="filter:genre")],
        [InlineKeyboardButton(text="📅 Yil / Year",          callback_data="filter:year")],
        [InlineKeyboardButton(text="🌍 Mamlakat / Country",  callback_data="filter:country")],
        [InlineKeyboardButton(text="🎤 Til / Language",      callback_data="filter:language")],
        [InlineKeyboardButton(text="⭐ Reyting / Rating",   callback_data="filter:rating")],
        home_row(lang),
    ])


def genres_kb(genres: List[str], lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = []
    GENRE_EMOJI = {
        "Action": "💥", "Boevik": "💥", "Drama": "🎭", "Comedy": "😂", "Komediya": "😂",
        "Thriller": "😱", "Triller": "😱", "Fantasy": "🧙", "Fantaziya": "🧙",
        "Sci-Fi": "🚀", "Fantastika": "🚀", "Horror": "👻", "Mistika": "👻",
        "Romance": "💕", "Romantika": "💕", "Crime": "🔫", "Jinoyat": "🔫",
        "Adventure": "⚔️", "Sarguzasht": "⚔️", "Animation": "🎨", "Animatsiya": "🎨",
        "Biography": "📖", "Biografiya": "📖", "History": "🏛", "Tarix": "🏛",
        "War": "🎖", "Urush": "🎖", "Music": "🎵", "Muzikl": "🎵", "Sport": "🏆",
        "Documentary": "📹", "Dokumentali": "📹",
    }
    row = []
    for i, g in enumerate(genres):
        emoji = GENRE_EMOJI.get(g, "🎬")
        row.append(InlineKeyboardButton(text=f"{emoji} {g}", callback_data=f"filter_genre:{g}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="filter_menu"),
        InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def rating_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    ratings = [("⭐ 5+", "5.0"), ("⭐ 6+", "6.0"), ("⭐ 7+", "7.0"), ("⭐ 8+", "8.0"), ("⭐ 9+", "9.0")]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=f"filter_rating:{value}") for label, value in ratings],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="filter_menu")],
    ])


def country_list_kb(countries: List[str], lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=c, callback_data=f"filter_country:{c}")] for c in countries[:30]]
    buttons.append([
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="filter_menu"),
        InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def language_list_kb(languages: List[str], lang: str = "uz") -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=l, callback_data=f"filter_language:{l}")] for l in languages[:20]]
    buttons.append([
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="filter_menu"),
        InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Favorites / History ────────────────────────────────────────────────────

def favorites_kb(
    movies: list,
    page: int,
    total: int,
    per_page: int,
    lang: str = "uz",
) -> InlineKeyboardMarkup:
    return movies_list_kb(
        movies, page, total, per_page,
        prefix="favpage",
        lang=lang,
    )


def history_kb(
    movies: list,
    page: int,
    total: int,
    per_page: int,
    lang: str = "uz",
) -> InlineKeyboardMarkup:
    buttons = []
    for movie in movies:
        title = movie.get_title(lang) if hasattr(movie, "get_title") else str(movie)
        movie_id = getattr(movie, "id", 0)
        buttons.append([InlineKeyboardButton(
            text=f"📽 {title}",
            callback_data=f"movie:{movie_id}",
        )])

    nav = pagination_row(page, total, per_page, "histpage", lang)
    if nav:
        buttons.append(nav)
    buttons.append([
        InlineKeyboardButton(text="🗑 Tarixni tozalash", callback_data="history:clear"),
        InlineKeyboardButton(text=t("btn_home", lang), callback_data="home"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── Settings ───────────────────────────────────────────────────────────────

def settings_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_change_lang", lang), callback_data="settings:change_lang")],
        [InlineKeyboardButton(text=t("btn_home", lang), callback_data="home")],
    ])


# ── Channel Guard ──────────────────────────────────────────────────────────

def channel_guard_kb(channel: str, lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Subscribe / Obuna", url=f"https://t.me/{channel.lstrip('@')}")],
        [InlineKeyboardButton(text=t("btn_check_sub", lang), callback_data="check_sub")],
    ])


# ── Admin ──────────────────────────────────────────────────────────────────

def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Kinolar",       callback_data="adm:movies"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="adm:users"),
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast",     callback_data="adm:broadcast"),
            InlineKeyboardButton(text="📊 Statistika",    callback_data="adm:stats"),
        ],
        [
            InlineKeyboardButton(text="📤 Export",        callback_data="adm:export"),
            InlineKeyboardButton(text="👮 Adminlar",       callback_data="adm:admins"),
        ],
        [InlineKeyboardButton(text="🏠 Bot Bosh Menyu",   callback_data="home")],
    ])


def admin_user_actions_kb(tg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 Block",       callback_data=f"adm_user:block:{tg_id}"),
            InlineKeyboardButton(text="✅ Unblock",     callback_data=f"adm_user:unblock:{tg_id}"),
        ],
        [
            InlineKeyboardButton(text="🔇 Mute",        callback_data=f"adm_user:mute:{tg_id}"),
            InlineKeyboardButton(text="⚠️ Warn",        callback_data=f"adm_user:warn:{tg_id}"),
        ],
        [
            InlineKeyboardButton(text="🔨 Ban",         callback_data=f"adm_user:ban:{tg_id}"),
            InlineKeyboardButton(text="⏳ Temp Ban",    callback_data=f"adm_user:tempban:{tg_id}"),
        ],
        [InlineKeyboardButton(text="◀️ Orqaga",          callback_data="adm:users")],
    ])


def admin_export_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Movies CSV",   callback_data="export:movies:csv"),
            InlineKeyboardButton(text="🎬 Movies XLSX",  callback_data="export:movies:xlsx"),
        ],
        [
            InlineKeyboardButton(text="🎬 Movies JSON",  callback_data="export:movies:json"),
        ],
        [
            InlineKeyboardButton(text="👥 Users CSV",    callback_data="export:users:csv"),
            InlineKeyboardButton(text="👥 Users XLSX",   callback_data="export:users:xlsx"),
        ],
        [
            InlineKeyboardButton(text="📊 Stats JSON",   callback_data="export:stats:json"),
        ],
        [InlineKeyboardButton(text="◀️ Admin panel",     callback_data="adm:menu")],
    ])


def broadcast_create_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Hozir yuborish",   callback_data="bc:now")],
        [InlineKeyboardButton(text="⏰ Vaqt belgilash",   callback_data="bc:schedule")],
        [InlineKeyboardButton(text="👁 Ko'rib chiqish",   callback_data="bc:preview")],
        [InlineKeyboardButton(text="❌ Bekor qilish",     callback_data="bc:cancel")],
    ])


# ── Misc ───────────────────────────────────────────────────────────────────

NOOP_KB = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="🏠 Home", callback_data="home")
]])
