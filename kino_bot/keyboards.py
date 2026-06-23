from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from data.movies import GENRES, MOVIES
from config import MOVIES_PER_PAGE


# ─────────────────────────────────────────
#  ASOSIY MENYU (Reply Keyboard)
# ─────────────────────────────────────────
def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🎬 Filmlar katalogi"),
        KeyboardButton("🔍 Qidirish"),
    )
    kb.add(
        KeyboardButton("⭐ Top filmlar"),
        KeyboardButton("🎭 Janr bo'yicha"),
    )
    kb.add(
        KeyboardButton("🎲 Tasodifiy film"),
        KeyboardButton("ℹ️ Bot haqida"),
    )
    return kb


# ─────────────────────────────────────────
#  FILMLAR RO'YXATI (sahifalash bilan)
# ─────────────────────────────────────────
def movies_list_kb(page: int = 0, movies: list = None) -> InlineKeyboardMarkup:
    if movies is None:
        movies = MOVIES

    total = len(movies)
    start = page * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE
    current_page_movies = movies[start:end]

    buttons = []

    # Har bir film tugmasi
    for movie in current_page_movies:
        stars = "⭐" * int(movie["rating"] // 2)
        btn_text = f"{movie['title_uz']} ({movie['year']}) {stars}"
        buttons.append([
            InlineKeyboardButton(
                text=btn_text,
                callback_data=f"movie_{movie['id']}"
            )
        ])

    # Navigatsiya tugmalari
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page - 1}"))

    nav_row.append(InlineKeyboardButton(
        f"📄 {page + 1}/{(total + MOVIES_PER_PAGE - 1) // MOVIES_PER_PAGE}",
        callback_data="noop"
    ))

    if end < total:
        nav_row.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"page_{page + 1}"))

    if nav_row:
        buttons.append(nav_row)

    # Ortga qaytish
    buttons.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────
#  FILM KARTOCHKASI
# ─────────────────────────────────────────
def movie_detail_kb(movie: dict) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton("▶️ Tomosha qilish", url=movie["watch_url"]),
            InlineKeyboardButton("🎞 Treyler", url=movie["trailer_url"]),
        ],
        [
            InlineKeyboardButton("📋 Barcha filmlar", callback_data="catalog"),
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────
#  JANRLAR MENYUSI
# ─────────────────────────────────────────
def genres_kb() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    genre_emojis = {
        "Boevik": "💥", "Animatsiya": "🎨", "Biografiya": "📖",
        "Drama": "🎭", "Dokumentali": "📹", "Fantastika": "🚀",
        "Fantaziya": "🧙", "Komediya": "😂", "Jinoyat": "🔫",
        "Mistika": "👻", "Muzikl": "🎵", "Romantika": "💕",
        "Sarguzasht": "⚔️", "Sport": "🏆", "Tarix": "🏛",
        "Triller": "😱", "Urush": "🎖",
    }
    for i, genre in enumerate(GENRES):
        emoji = genre_emojis.get(genre, "🎬")
        row.append(InlineKeyboardButton(f"{emoji} {genre}", callback_data=f"genre_{genre}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────
#  JANR NATIJALARI
# ─────────────────────────────────────────
def genre_results_kb(movies: list, genre: str) -> InlineKeyboardMarkup:
    buttons = []
    for movie in movies:
        buttons.append([
            InlineKeyboardButton(
                f"🎬 {movie['title_uz']} ({movie['year']}) ⭐{movie['rating']}",
                callback_data=f"movie_{movie['id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton("🎭 Janrlar", callback_data="genres"),
        InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────
#  QIDIRUV NATIJALARI
# ─────────────────────────────────────────
def search_results_kb(movies: list) -> InlineKeyboardMarkup:
    buttons = []
    for movie in movies:
        buttons.append([
            InlineKeyboardButton(
                f"🎬 {movie['title_uz']} ({movie['year']}) ⭐{movie['rating']}",
                callback_data=f"movie_{movie['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ─────────────────────────────────────────
#  TOP FILMLAR
# ─────────────────────────────────────────
def top_movies_kb(movies: list) -> InlineKeyboardMarkup:
    buttons = []
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for i, movie in enumerate(movies):
        medal = medals[i] if i < len(medals) else "🎬"
        buttons.append([
            InlineKeyboardButton(
                f"{medal} {movie['title_uz']} — ⭐{movie['rating']}",
                callback_data=f"movie_{movie['id']}"
            )
        ])
    buttons.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
