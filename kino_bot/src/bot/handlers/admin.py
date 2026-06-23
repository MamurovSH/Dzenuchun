"""
Admin panel handler (#10, #14, #15, #21, #22, #11).
Covers: Multi-Admin roles, User management, Broadcast, Stats, Export.
"""
from __future__ import annotations

import asyncio
import io
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile, CallbackQuery, Message,
)

from src.bot.filters.admin_filter import IsAdmin, HasPermission
from src.bot.keyboards import (
    admin_export_kb, admin_main_kb, admin_user_actions_kb, broadcast_create_kb,
    main_menu_kb,
)
from src.core.config import settings
from src.core.security import verify_2fa_code
from src.db.base import AsyncSessionFactory
from src.db.models.admin import AdminRole
from src.db.models.broadcast import BroadcastStatus
from src.db.repositories.admin_repo import AdminRepository
from src.db.repositories.broadcast_repo import BroadcastRepository
from src.db.repositories.movie_repo import MovieRepository
from src.db.repositories.user_repo import UserRepository
from src.services.broadcast import BroadcastService
from src.services.export import ExportService
from src.utils.formatters import format_stats, format_user_info

logger = logging.getLogger(__name__)
router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ── FSM States ─────────────────────────────────────────────────────────────

class AdminFSM(StatesGroup):
    # 2FA
    waiting_2fa_code = State()
    # User management
    waiting_user_lookup = State()
    waiting_ban_reason = State()
    waiting_tempban_days = State()
    waiting_mute_hours = State()
    # Add admin
    waiting_new_admin_id = State()
    waiting_new_admin_role = State()
    # Broadcast
    waiting_bc_text = State()
    waiting_bc_schedule = State()
    # Add movie
    waiting_movie_code = State()


# ── ADMIN PANEL ENTRY ──────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, admin=None, state: FSMContext = None):
    if admin and admin.totp_enabled and not admin.is_2fa_verified:
        await state.set_state(AdminFSM.waiting_2fa_code)
        await message.answer("🔐 <b>2FA kodni kiriting:</b>")
        return
    await message.answer("👮 <b>Admin Panel</b>", reply_markup=admin_main_kb())


@router.message(AdminFSM.waiting_2fa_code)
async def process_2fa(message: Message, state: FSMContext, admin=None):
    code = (message.text or "").strip()
    if admin and verify_2fa_code(admin.totp_secret, code):
        async with AsyncSessionFactory() as session:
            repo = AdminRepository(session)
            await repo.set_2fa_verified(message.from_user.id, True)
            await session.commit()
        await state.clear()
        await message.answer("✅ 2FA tasdiqlandi!", reply_markup=admin_main_kb())
    else:
        await message.answer("❌ Noto'g'ri kod. Qayta urining:")


@router.callback_query(F.data == "adm:menu")
async def cb_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text("👮 <b>Admin Panel</b>", reply_markup=admin_main_kb())
    await callback.answer()


# ── STATISTICS (#22) ───────────────────────────────────────────────────────

@router.callback_query(F.data == "adm:stats")
async def cb_admin_stats(callback: CallbackQuery):
    async with AsyncSessionFactory() as session:
        movie_count = await MovieRepository(session).count_total()
        user_count = await UserRepository(session).count_total()
        active_today = await UserRepository(session).count_active_today()

    stats = {
        "total_movies": movie_count,
        "total_users": user_count,
        "active_today": active_today,
    }
    text = format_stats(stats)
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:menu")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# ── EXPORT (#11) ───────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm:export")
async def cb_admin_export(callback: CallbackQuery):
    await callback.message.edit_text("📤 <b>Export tanlang:</b>", reply_markup=admin_export_kb())
    await callback.answer()


@router.callback_query(F.data.startswith("export:"))
async def cb_do_export(callback: CallbackQuery, admin=None):
    parts = callback.data.split(":")
    entity = parts[1]   # movies | users | stats
    fmt = parts[2]       # csv | xlsx | json

    await callback.answer("⏳ Tayyorlanmoqda...", show_alert=False)

    exporter = ExportService()

    if entity == "movies":
        async with AsyncSessionFactory() as session:
            movies, _ = await MovieRepository(session).get_all(page=0, per_page=10000)
        if fmt == "csv":
            data = exporter.movies_to_csv(movies)
            fname = "movies.csv"
            mime = "text/csv"
        elif fmt == "xlsx":
            data = exporter.movies_to_excel(movies)
            fname = "movies.xlsx"
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            data = exporter.movies_to_json(movies)
            fname = "movies.json"
            mime = "application/json"

    elif entity == "users":
        async with AsyncSessionFactory() as session:
            users, _ = await UserRepository(session).get_page(page=0, per_page=100000)
        if fmt == "csv":
            data = exporter.users_to_csv(users)
            fname = "users.csv"
            mime = "text/csv"
        else:
            data = exporter.users_to_excel(users)
            fname = "users.xlsx"
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    else:  # stats
        async with AsyncSessionFactory() as session:
            movie_count = await MovieRepository(session).count_total()
            user_count = await UserRepository(session).count_total()
        data = exporter.stats_to_json({"total_movies": movie_count, "total_users": user_count})
        fname = "stats.json"
        mime = "application/json"

    file = BufferedInputFile(data, filename=fname)
    await callback.message.answer_document(file, caption=f"📤 {fname}")


# ── USERS MANAGEMENT (#14) ─────────────────────────────────────────────────

@router.callback_query(F.data == "adm:users")
async def cb_admin_users(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminFSM.waiting_user_lookup)
    await callback.message.answer(
        "👥 Foydalanuvchi Telegram ID sini kiriting:"
    )
    await callback.answer()


@router.message(AdminFSM.waiting_user_lookup)
async def process_user_lookup(message: Message, state: FSMContext):
    await state.clear()
    try:
        tg_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Faqat raqam kiriting")
        return

    async with AsyncSessionFactory() as session:
        user = await UserRepository(session).get_by_telegram_id(tg_id)

    if not user:
        await message.answer("😔 Foydalanuvchi topilmadi")
        return

    text = format_user_info(user)
    await message.answer(text, reply_markup=admin_user_actions_kb(tg_id))


@router.callback_query(F.data.startswith("adm_user:"))
async def cb_user_action(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    action = parts[1]
    tg_id = int(parts[2])

    async with AsyncSessionFactory() as session:
        user_repo = UserRepository(session)

        if action == "block":
            await user_repo.block_user(tg_id, reason="Admin tomonidan bloklandi")
            await session.commit()
            await callback.answer("✅ Bloklandi", show_alert=True)

        elif action == "unblock":
            await user_repo.unblock_user(tg_id)
            await session.commit()
            await callback.answer("✅ Blok olib tashlandi", show_alert=True)

        elif action == "warn":
            count = await user_repo.warn_user(tg_id)
            await session.commit()
            await callback.answer(f"⚠️ Ogohlantirish #{count} berildi", show_alert=True)

        elif action == "ban":
            await user_repo.ban_user(tg_id, reason="Admin tomonidan ban qilindi")
            await session.commit()
            await callback.answer("🚫 Ban qilindi", show_alert=True)

        elif action == "mute":
            mute_until = datetime.now(timezone.utc) + timedelta(hours=24)
            await user_repo.mute_user(tg_id, mute_until)
            await session.commit()
            await callback.answer("🔇 24 soatga muzlatildi", show_alert=True)

        elif action == "tempban":
            ban_until = datetime.now(timezone.utc) + timedelta(days=7)
            await user_repo.temp_ban_user(tg_id, ban_until, reason="Vaqtinchalik ban")
            await session.commit()
            await callback.answer("⏳ 7 kunlik ban berildi", show_alert=True)


# ── BROADCAST (#15) ────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminFSM.waiting_bc_text)
    await callback.message.answer(
        "📢 <b>Broadcast matni:</b>\n\n"
        "HTML formatda yozing. Bekor qilish: /cancel"
    )
    await callback.answer()


@router.message(AdminFSM.waiting_bc_text)
async def process_bc_text(message: Message, state: FSMContext):
    text = message.text or message.caption or ""
    await state.update_data(bc_text=text)
    await state.clear()
    await message.answer(
        f"👁 <b>Preview:</b>\n\n{text}\n\nYuborishni tasdiqlaysizmi?",
        reply_markup=broadcast_create_kb(),
    )


@router.callback_query(F.data == "bc:now")
async def cb_broadcast_now(callback: CallbackQuery, state: FSMContext, admin=None):
    data = await state.get_data()
    text = data.get("bc_text", "")
    if not text:
        await callback.answer("❌ Matn topilmadi", show_alert=True)
        return

    async with AsyncSessionFactory() as session:
        bc_repo = BroadcastRepository(session)
        bc = await bc_repo.create(
            title="Manual Broadcast",
            text=text,
            created_by=callback.from_user.id,
        )
        await bc_repo.set_status(bc.id, BroadcastStatus.SCHEDULED)
        await bc_repo.update_stats(bc.id, 0, 0)
        bc_id = bc.id
        await session.commit()

    await callback.answer("📢 Broadcast boshlandi!", show_alert=True)
    service = BroadcastService(callback.bot)

    async with AsyncSessionFactory() as session:
        bc = await BroadcastRepository(session).get_by_id(bc_id)

    asyncio.create_task(service.execute(bc))


@router.callback_query(F.data == "bc:cancel")
async def cb_broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("❌ Bekor qilindi")
    await callback.message.edit_text("❌ Broadcast bekor qilindi.", reply_markup=admin_main_kb())


# ── ADD / MANAGE ADMINS (#10) ──────────────────────────────────────────────

@router.callback_query(F.data == "adm:admins")
async def cb_admin_list(callback: CallbackQuery):
    async with AsyncSessionFactory() as session:
        admins = await AdminRepository(session).get_all()

    text = "👮 <b>Admin ro'yxati:</b>\n\n"
    for adm in admins:
        text += f"• {adm.full_name} (@{adm.username or '?'}) — <b>{adm.role.value}</b>\n"

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="adm:add_admin")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="adm:menu")],
    ])
    await callback.message.edit_text(text or "Bo'sh", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "adm:add_admin")
async def cb_add_admin(callback: CallbackQuery, state: FSMContext, admin=None):
    if not admin or admin.role.value != "super_admin":
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await state.set_state(AdminFSM.waiting_new_admin_id)
    await callback.message.answer(
        "👮 Yangi admin Telegram ID sini kiriting:\n\n"
        "Role: support | moderator | admin"
    )
    await callback.answer()


@router.message(AdminFSM.waiting_new_admin_id)
async def process_new_admin(message: Message, state: FSMContext):
    parts = message.text.strip().split()
    try:
        tg_id = int(parts[0])
        role_str = parts[1] if len(parts) > 1 else "support"
        role = AdminRole(role_str)
    except (ValueError, IndexError):
        await message.answer("❌ Format: <tg_id> <role>\nMisol: 123456789 moderator")
        return

    await state.clear()
    async with AsyncSessionFactory() as session:
        admin_repo = AdminRepository(session)
        if await admin_repo.exists(tg_id):
            await message.answer("ℹ️ Bu foydalanuvchi allaqachon admin")
            return
        adm = await admin_repo.create(
            telegram_id=tg_id,
            full_name=f"Admin {tg_id}",
            role=role,
            added_by=message.from_user.id,
        )
        await session.commit()
    await message.answer(f"✅ Admin qo'shildi: {tg_id} ({role.value})")
