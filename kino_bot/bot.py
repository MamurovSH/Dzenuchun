"""
╔══════════════════════════════════════════╗
║          🎬  KINO BOT  🎬                ║
║   Telegram bot — Filmlar katalogi        ║
║   Yaratuvchi: @MamurovSH                 ║
╚══════════════════════════════════════════╝

Ishga tushirish:
    pip install -r requirements.txt
    BOT_TOKEN=your_token python bot.py
"""

import logging
import random
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from config import BOT_TOKEN, ADMIN_ID, BOT_NAME, MOVIES_PER_PAGE
from data.movies import (
    get_all_movies,
    get_movie_by_id,
    search_movies,
    get_movies_by_genre,
    get_top_movies,
    MOVIES,
)
from keyboards import (
    main_menu_kb,
    movies_list_kb,
    movie_detail_kb,
    genres_kb,
    genre_results_kb,
    search_results_kb,
    top_movies_kb,
)

# ─── Logging sozlamalari ───────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Bot va Dispatcher ────────────────────────────────────────
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# ─── FSM holatlari ────────────────────────────────────────────
class SearchState(StatesGroup):
    waiting_for_query = State()


# ─────────────────────────────────────────────────────────────
#  YORDAM FUNKSIYALARI
# ─────────────────────────────────────────────────────────────

def format_movie_card(movie: dict) -> str:
    """Film kartochkasini HTML formatda qaytaradi"""
    genres = " | ".join(movie["genre"])
    tags = "  ".join([f"#{t}" for t in movie["tags"]])
    stars = "⭐" * round(movie["rating"] / 2)

    return (
        f"🎬 <b>{movie['title']}</b>\n"
        f"🇺🇿 <i>{movie['title_uz']}</i>\n\n"
        f"📅 <b>Yil:</b> {movie['year']}\n"
        f"🎭 <b>Janr:</b> {genres}\n"
        f"🎬 <b>Rejissyor:</b> {movie['director']}\n"
        f"⏱ <b>Davomiyligi:</b> {movie['duration']}\n"
        f"🌍 <b>Mamlakat:</b> {movie['country']}\n"
        f"🗣 <b>Til:</b> {movie['language']}\n"
        f"⭐ <b>Reyting:</b> {movie['rating']}/10  {stars}\n\n"
        f"📝 <b>Qisqacha:</b>\n{movie['description']}\n\n"
        f"🏷 {tags}"
    )


# ─────────────────────────────────────────────────────────────
#  /start  BUYRUG'I
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user = message.from_user
    logger.info(f"Yangi foydalanuvchi: {user.id} | {user.full_name}")

    welcome_text = (
        f"👋 Salom, <b>{user.first_name}</b>!\n\n"
        f"🎬 <b>{BOT_NAME}</b> ga xush kelibsiz!\n\n"
        f"📽 Men sizga eng yaxshi filmlarni topishga yordam beraman:\n"
        f"  🔍 Film nomini yozing — topa olaman\n"
        f"  🎭 Janr bo'yicha saralash\n"
        f"  ⭐ Top reytingli filmlar\n"
        f"  🎲 Tasodifiy film tavsiyasi\n\n"
        f"Quyidagi menyudan tanlang 👇"
    )
    await message.answer(welcome_text, reply_markup=main_menu_kb())


# ─────────────────────────────────────────────────────────────
#  /help  BUYRUG'I
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    help_text = (
        "📖 <b>Bot buyruqlari:</b>\n\n"
        "/start — Botni qayta ishga tushirish\n"
        "/catalog — Filmlar katalogi\n"
        "/top — Top 5 film\n"
        "/random — Tasodifiy film\n"
        "/search — Film qidirish\n"
        "/help — Yordam\n\n"
        "🔍 <b>Qidirish:</b>\n"
        "Film nomini, rejissyor nomini yoki kalit so'z yozing\n\n"
        "❓ Savol bo'lsa admin bilan bog'laning: @MamurovSH"
    )
    await message.answer(help_text, reply_markup=main_menu_kb())


# ─────────────────────────────────────────────────────────────
#  /catalog  —  FILMLAR KATALOGI
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["catalog"])
@dp.message_handler(lambda m: m.text == "🎬 Filmlar katalogi")
async def cmd_catalog(message: types.Message):
    movies = get_all_movies()
    text = (
        f"📋 <b>Filmlar katalogi</b>\n"
        f"Jami: <b>{len(movies)} ta</b> film mavjud\n\n"
        f"Quyidan filmni tanlang 👇"
    )
    await message.answer(text, reply_markup=movies_list_kb(page=0))


# ─────────────────────────────────────────────────────────────
#  ⭐ TOP FILMLAR
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["top"])
@dp.message_handler(lambda m: m.text == "⭐ Top filmlar")
async def cmd_top(message: types.Message):
    movies = get_top_movies(5)
    text = "🏆 <b>Top 5 — Eng yaxshi filmlar</b>\n\n"
    for i, movie in enumerate(movies, 1):
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        medal = medals.get(i, f"{i}.")
        text += f"{medal} <b>{movie['title_uz']}</b> — ⭐ {movie['rating']}/10\n"

    await message.answer(text, reply_markup=top_movies_kb(movies))


# ─────────────────────────────────────────────────────────────
#  🎭 JANR BO'YICHA
# ─────────────────────────────────────────────────────────────

@dp.message_handler(lambda m: m.text == "🎭 Janr bo'yicha")
async def cmd_genres(message: types.Message):
    await message.answer(
        "🎭 <b>Janrni tanlang:</b>",
        reply_markup=genres_kb()
    )


# ─────────────────────────────────────────────────────────────
#  🎲 TASODIFIY FILM
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["random"])
@dp.message_handler(lambda m: m.text == "🎲 Tasodifiy film")
async def cmd_random(message: types.Message):
    movie = random.choice(MOVIES)
    text = "🎲 <b>Bugungi tavsiya:</b>\n\n" + format_movie_card(movie)
    await message.answer(text, reply_markup=movie_detail_kb(movie))


# ─────────────────────────────────────────────────────────────
#  🔍 QIDIRISH
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["search"])
@dp.message_handler(lambda m: m.text == "🔍 Qidirish")
async def cmd_search(message: types.Message):
    await SearchState.waiting_for_query.set()
    await message.answer(
        "🔍 <b>Qidirish</b>\n\n"
        "Film nomi, rejissyor yoki kalit so'z yozing:\n"
        "<i>(Bekor qilish uchun /cancel yozing)</i>",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message_handler(commands=["cancel"], state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_kb())


@dp.message_handler(state=SearchState.waiting_for_query)
async def process_search(message: types.Message, state: FSMContext):
    await state.finish()
    query = message.text.strip()

    if len(query) < 2:
        await message.answer("⚠️ Kamida 2 ta harf kiriting.", reply_markup=main_menu_kb())
        return

    results = search_movies(query)

    if not results:
        await message.answer(
            f"😔 <b>«{query}»</b> bo'yicha hech narsa topilmadi.\n\n"
            "Boshqa so'z bilan qidirib ko'ring.",
            reply_markup=main_menu_kb()
        )
        return

    text = f"🔍 <b>«{query}»</b> bo'yicha natijalar:\n<i>Topildi: {len(results)} ta film</i>"
    await message.answer(text, reply_markup=search_results_kb(results))


# ─────────────────────────────────────────────────────────────
#  ℹ️ BOT HAQIDA
# ─────────────────────────────────────────────────────────────

@dp.message_handler(lambda m: m.text == "ℹ️ Bot haqida")
async def cmd_about(message: types.Message):
    about_text = (
        f"🎬 <b>{BOT_NAME}</b>\n\n"
        f"📽 <b>Nima qiladi?</b>\n"
        f"• Filmlar katalogi va qidirish\n"
        f"• Janr bo'yicha saralash\n"
        f"• Reyting bo'yicha top filmlar\n"
        f"• Tasodifiy film tavsiyasi\n"
        f"• Treyler va tomosha havolalari\n\n"
        f"📊 <b>Statistika:</b>\n"
        f"• Filmlar soni: {len(MOVIES)} ta\n\n"
        f"👨‍💻 <b>Yaratuvchi:</b> @MamurovSH\n"
        f"🔧 <b>Texnologiya:</b> Python + aiogram"
    )
    await message.answer(about_text, reply_markup=main_menu_kb())


# ─────────────────────────────────────────────────────────────
#  CALLBACK QUERY HANDLERLARI
# ─────────────────────────────────────────────────────────────

@dp.callback_query_handler(lambda c: c.data == "noop")
async def cb_noop(callback: types.CallbackQuery):
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def cb_main_menu(callback: types.CallbackQuery):
    await callback.message.answer("🏠 Bosh menyu:", reply_markup=main_menu_kb())
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "catalog")
async def cb_catalog(callback: types.CallbackQuery):
    movies = get_all_movies()
    text = (
        f"📋 <b>Filmlar katalogi</b>\n"
        f"Jami: <b>{len(movies)} ta</b> film\n\n"
        "Filmni tanlang 👇"
    )
    await callback.message.edit_text(text, reply_markup=movies_list_kb(page=0))
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data == "genres")
async def cb_genres(callback: types.CallbackQuery):
    await callback.message.edit_text("🎭 <b>Janrni tanlang:</b>", reply_markup=genres_kb())
    await callback.answer()


# Sahifalash
@dp.callback_query_handler(lambda c: c.data.startswith("page_"))
async def cb_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[1])
    movies = get_all_movies()
    text = (
        f"📋 <b>Filmlar katalogi</b>\n"
        f"Jami: <b>{len(movies)} ta</b> film\n\n"
        "Filmni tanlang 👇"
    )
    await callback.message.edit_text(text, reply_markup=movies_list_kb(page=page))
    await callback.answer()


# Film kartochkasi
@dp.callback_query_handler(lambda c: c.data.startswith("movie_"))
async def cb_movie_detail(callback: types.CallbackQuery):
    movie_id = int(callback.data.split("_")[1])
    movie = get_movie_by_id(movie_id)

    if not movie:
        await callback.answer("❌ Film topilmadi!", show_alert=True)
        return

    text = format_movie_card(movie)
    await callback.message.answer(text, reply_markup=movie_detail_kb(movie))
    await callback.answer()


# Janr bo'yicha
@dp.callback_query_handler(lambda c: c.data.startswith("genre_"))
async def cb_genre(callback: types.CallbackQuery):
    genre = callback.data.split("_", 1)[1]
    movies = get_movies_by_genre(genre)

    if not movies:
        await callback.answer(f"😔 {genre} janrida hozircha filmlar yo'q", show_alert=True)
        return

    text = (
        f"🎭 <b>{genre}</b> janridagi filmlar:\n"
        f"<i>Topildi: {len(movies)} ta</i>"
    )
    await callback.message.edit_text(text, reply_markup=genre_results_kb(movies, genre))
    await callback.answer()


# ─────────────────────────────────────────────────────────────
#  NOMA'LUM XABARLAR
# ─────────────────────────────────────────────────────────────

@dp.message_handler()
async def unknown_message(message: types.Message):
    # Avval qidirish sifatida urinib ko'ramiz
    query = message.text.strip()
    if len(query) >= 2:
        results = search_movies(query)
        if results:
            text = (
                f"🔍 <b>«{query}»</b> bo'yicha topildi:\n"
                f"<i>{len(results)} ta film</i>"
            )
            await message.answer(text, reply_markup=search_results_kb(results))
            return

    await message.answer(
        "❓ Tushunmadim. Menyudan tanlang yoki film nomini yozing:",
        reply_markup=main_menu_kb()
    )


# ─────────────────────────────────────────────────────────────
#  ADMIN: /stats
# ─────────────────────────────────────────────────────────────

@dp.message_handler(commands=["stats"])
async def cmd_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Bu buyruq faqat admin uchun.")
        return

    await message.answer(
        f"📊 <b>Bot statistikasi:</b>\n\n"
        f"🎬 Filmlar soni: <b>{len(MOVIES)}</b>\n"
        f"✅ Bot ishlayapti!"
    )


# ─────────────────────────────────────────────────────────────
#  ISHGA TUSHIRISH
# ─────────────────────────────────────────────────────────────

async def on_startup(dp):
    logger.info("═" * 50)
    logger.info(f"  🎬 {BOT_NAME} ishga tushdi!")
    logger.info(f"  📽 Filmlar soni: {len(MOVIES)}")
    logger.info("═" * 50)


async def on_shutdown(dp):
    logger.info("🛑 Bot to'xtatildi.")
    await storage.close()
    await storage.wait_closed()


if __name__ == "__main__":
    executor.start_polling(
        dp,
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
    )
