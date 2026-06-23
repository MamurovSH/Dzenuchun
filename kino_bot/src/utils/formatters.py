"""
Formatting helpers — movie cards, user info, admin stats.
"""
from __future__ import annotations

from typing import Any

from src.db.models.movie import Movie
from src.db.models.user import User


def format_movie_card(movie: Movie, lang: str = "uz") -> str:
    title = movie.get_title(lang)
    description = movie.get_description(lang)
    genres = ", ".join(movie.genres or [])
    tags = "  ".join(f"#{t}" for t in (movie.tags or []))
    stars = "⭐" * round(movie.rating / 2)

    lines = [
        f"🎬 <b>{title}</b>",
        f"🔑 <code>{movie.code}</code>",
        "",
        f"📅 <b>Yil / Year:</b> {movie.year}",
    ]
    if genres:
        lines.append(f"🎭 <b>Janr / Genre:</b> {genres}")
    if movie.director:
        lines.append(f"🎬 <b>Rejissyor / Director:</b> {movie.director}")
    if movie.duration:
        lines.append(f"⏱ <b>Davomiylik / Duration:</b> {movie.duration}")
    if movie.country:
        lines.append(f"🌍 <b>Mamlakat / Country:</b> {movie.country}")
    if movie.language:
        lines.append(f"🗣 <b>Til / Language:</b> {movie.language}")
    lines.append(f"⭐ <b>Reyting:</b> {movie.rating}/10  {stars}")
    lines.append(f"👁 <b>Ko'rilgan:</b> {movie.view_count:,} marta")
    if description:
        lines += ["", f"📝 <b>Qisqacha:</b>", description]
    if tags:
        lines += ["", tags]

    return "\n".join(lines)


def format_user_info(user: User) -> str:
    lines = [
        f"👤 <b>{user.full_name}</b>",
        f"🆔 ID: <code>{user.telegram_id}</code>",
    ]
    if user.username:
        lines.append(f"📱 @{user.username}")
    lines += [
        f"🌍 Til: <b>{user.language.value.upper()}</b>",
        f"📊 Status: <b>{user.status.value}</b>",
        f"🔍 Qidiruvlar: <b>{user.total_searches}</b>",
        f"👁 Ko'rishlar: <b>{user.total_views}</b>",
        f"⚠️ Ogohlantirish: <b>{user.warn_count}</b>",
    ]
    if user.ban_reason:
        lines.append(f"🚫 Sabab: {user.ban_reason}")
    if user.ban_until:
        lines.append(f"⏳ Ban tugaydi: {user.ban_until.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"📅 Qo'shilgan: {user.created_at.strftime('%Y-%m-%d') if user.created_at else '—'}")
    return "\n".join(lines)


def format_stats(stats: dict) -> str:
    return (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats.get('total_users', 0):,}</b>\n"
        f"📅 Bugun faol: <b>{stats.get('active_today', 0):,}</b>\n"
        f"🎬 Jami kinolar: <b>{stats.get('total_movies', 0):,}</b>\n"
        f"🔍 Jami qidiruvlar: <b>{stats.get('total_searches', 0):,}</b>\n"
        f"👁 Jami ko'rishlar: <b>{stats.get('total_views', 0):,}</b>\n"
    )
