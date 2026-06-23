"""
Lightweight i18n system.
All UI strings are stored here in three languages.
Usage:
    t("welcome", lang="uz", name="Ali")
"""
from __future__ import annotations

from string import Template
from typing import Any

TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── ONBOARDING ─────────────────────────────────────────────────────────
    "choose_language": {
        "uz": "🌍 Tilni tanlang / Выберите язык / Choose language:",
        "ru": "🌍 Tilni tanlang / Выберите язык / Choose language:",
        "en": "🌍 Tilni tanlang / Выберите язык / Choose language:",
    },
    "language_set": {
        "uz": "✅ Til o'zbekchaga o'rnatildi!",
        "ru": "✅ Язык установлен на русский!",
        "en": "✅ Language set to English!",
    },
    "welcome": {
        "uz": (
            "👋 Salom, <b>$name</b>!\n\n"
            "🎬 <b>Kino Bot Enterprise</b> ga xush kelibsiz!\n\n"
            "📽 Nima qila olaman:\n"
            "  🔍 Kino kodi, nomi yoki kalit so'z bilan qidirish\n"
            "  🎭 Janr, yil, mamlakat, til bo'yicha filtrlash\n"
            "  ⭐ Top kinolar haftalik / oylik / yillik\n"
            "  ❤️ Sevimlilar ro'yxatini yuritish\n"
            "  📜 Ko'rish tarixi\n\n"
            "Quyidagi menyudan tanlang 👇"
        ),
        "ru": (
            "👋 Привет, <b>$name</b>!\n\n"
            "🎬 Добро пожаловать в <b>Kino Bot Enterprise</b>!\n\n"
            "📽 Что я умею:\n"
            "  🔍 Поиск по коду, названию или ключевому слову\n"
            "  🎭 Фильтрация по жанру, году, стране, языку\n"
            "  ⭐ Топ фильмов — еженедельно / ежемесячно / ежегодно\n"
            "  ❤️ Список избранного\n"
            "  📜 История просмотров\n\n"
            "Выберите в меню ниже 👇"
        ),
        "en": (
            "👋 Hello, <b>$name</b>!\n\n"
            "🎬 Welcome to <b>Kino Bot Enterprise</b>!\n\n"
            "📽 What I can do:\n"
            "  🔍 Search by code, title or keyword\n"
            "  🎭 Filter by genre, year, country, language\n"
            "  ⭐ Top movies — weekly / monthly / yearly\n"
            "  ❤️ Manage your favourites\n"
            "  📜 Watch history\n\n"
            "Choose from the menu below 👇"
        ),
    },

    # ── MAIN MENU BUTTONS ──────────────────────────────────────────────────
    "btn_catalog":    {"uz": "🎬 Katalog",        "ru": "🎬 Каталог",       "en": "🎬 Catalog"},
    "btn_search":     {"uz": "🔍 Qidirish",       "ru": "🔍 Поиск",         "en": "🔍 Search"},
    "btn_filter":     {"uz": "🎛 Filtrlash",      "ru": "🎛 Фильтр",        "en": "🎛 Filter"},
    "btn_top":        {"uz": "⭐ Top kinolar",    "ru": "⭐ Топ фильмов",   "en": "⭐ Top Movies"},
    "btn_recent":     {"uz": "🆕 Yangi kinolar",  "ru": "🆕 Новые фильмы",  "en": "🆕 Recent Movies"},
    "btn_favorites":  {"uz": "❤️ Sevimlilar",     "ru": "❤️ Избранное",     "en": "❤️ Favourites"},
    "btn_history":    {"uz": "📜 Tarix",           "ru": "📜 История",        "en": "📜 History"},
    "btn_settings":   {"uz": "⚙️ Sozlamalar",     "ru": "⚙️ Настройки",     "en": "⚙️ Settings"},
    "btn_about":      {"uz": "ℹ️ Bot haqida",     "ru": "ℹ️ О боте",         "en": "ℹ️ About"},
    "btn_back":       {"uz": "◀️ Orqaga",          "ru": "◀️ Назад",          "en": "◀️ Back"},
    "btn_home":       {"uz": "🏠 Bosh menyu",      "ru": "🏠 Главное меню",   "en": "🏠 Home"},
    "btn_next":       {"uz": "Keyingi ▶️",          "ru": "Далее ▶️",          "en": "Next ▶️"},
    "btn_prev":       {"uz": "◀️ Oldingi",          "ru": "◀️ Назад",          "en": "◀️ Previous"},
    "btn_cancel":     {"uz": "❌ Bekor qilish",    "ru": "❌ Отмена",         "en": "❌ Cancel"},
    "btn_confirm":    {"uz": "✅ Tasdiqlash",      "ru": "✅ Подтвердить",    "en": "✅ Confirm"},
    "btn_watch":      {"uz": "▶️ Tomosha qilish", "ru": "▶️ Смотреть",      "en": "▶️ Watch"},
    "btn_trailer":    {"uz": "🎞 Treyler",         "ru": "🎞 Трейлер",        "en": "🎞 Trailer"},
    "btn_fav_add":    {"uz": "❤️ Saqlash",         "ru": "❤️ Сохранить",      "en": "❤️ Save"},
    "btn_fav_remove": {"uz": "💔 O'chirish",       "ru": "💔 Удалить",        "en": "💔 Remove"},
    "btn_share":      {"uz": "🔗 Ulashish",        "ru": "🔗 Поделиться",     "en": "🔗 Share"},
    "btn_search_again":{"uz":"🔍 Qayta qidirish", "ru": "🔍 Найти снова",    "en": "🔍 Search Again"},

    # ── SEARCH ─────────────────────────────────────────────────────────────
    "search_prompt": {
        "uz": (
            "🔍 <b>Qidirish</b>\n\n"
            "Quyidagilardan birini kiriting:\n"
            "• Kino kodi (masalan: <code>TIT001</code>)\n"
            "• O'zbekcha, ruscha yoki inglizcha nomi\n"
            "• Qisman nomi (masalan: <code>Titan</code>)\n\n"
            "<i>Bekor qilish: /cancel</i>"
        ),
        "ru": (
            "🔍 <b>Поиск</b>\n\n"
            "Введите одно из следующего:\n"
            "• Код фильма (например: <code>TIT001</code>)\n"
            "• Название на узбекском, русском или английском\n"
            "• Часть названия (например: <code>Titan</code>)\n\n"
            "<i>Отмена: /cancel</i>"
        ),
        "en": (
            "🔍 <b>Search</b>\n\n"
            "Enter any of the following:\n"
            "• Movie code (e.g. <code>TIT001</code>)\n"
            "• Uzbek, Russian or English title\n"
            "• Partial title (e.g. <code>Titan</code>)\n\n"
            "<i>Cancel: /cancel</i>"
        ),
    },
    "search_too_short": {
        "uz": "⚠️ Kamida 2 ta belgi kiriting.",
        "ru": "⚠️ Введите минимум 2 символа.",
        "en": "⚠️ Please enter at least 2 characters.",
    },
    "search_no_results": {
        "uz": "😔 <b>«$query»</b> bo'yicha hech narsa topilmadi.\n\nBoshqa so'z bilan urinib ko'ring.",
        "ru": "😔 По запросу <b>«$query»</b> ничего не найдено.\n\nПопробуйте другой запрос.",
        "en": "😔 Nothing found for <b>«$query»</b>.\n\nTry a different search term.",
    },
    "search_results": {
        "uz": "🔍 <b>«$query»</b> bo'yicha <b>$count</b> ta natija topildi:",
        "ru": "🔍 По запросу <b>«$query»</b> найдено <b>$count</b> фильмов:",
        "en": "🔍 Found <b>$count</b> result(s) for <b>«$query»</b>:",
    },
    "search_cancelled": {
        "uz": "❌ Qidiruv bekor qilindi.",
        "ru": "❌ Поиск отменён.",
        "en": "❌ Search cancelled.",
    },

    # ── FILTER ─────────────────────────────────────────────────────────────
    "filter_choose_genre": {
        "uz": "🎬 <b>Janrni tanlang:</b>",
        "ru": "🎬 <b>Выберите жанр:</b>",
        "en": "🎬 <b>Choose genre:</b>",
    },
    "filter_choose_year": {
        "uz": "📅 <b>Yilni kiriting</b> (masalan: <code>2020</code> yoki <code>2010-2020</code>):",
        "ru": "📅 <b>Введите год</b> (например: <code>2020</code> или <code>2010-2020</code>):",
        "en": "📅 <b>Enter year</b> (e.g. <code>2020</code> or <code>2010-2020</code>):",
    },
    "filter_choose_country": {
        "uz": "🌍 <b>Mamlakatni tanlang:</b>",
        "ru": "🌍 <b>Выберите страну:</b>",
        "en": "🌍 <b>Choose country:</b>",
    },
    "filter_choose_language": {
        "uz": "🎤 <b>Tilni tanlang:</b>",
        "ru": "🎤 <b>Выберите язык фильма:</b>",
        "en": "🎤 <b>Choose film language:</b>",
    },
    "filter_choose_rating": {
        "uz": "⭐ <b>Minimal reytingni tanlang:</b>",
        "ru": "⭐ <b>Выберите минимальный рейтинг:</b>",
        "en": "⭐ <b>Choose minimum rating:</b>",
    },
    "filter_no_results": {
        "uz": "😔 Ushbu filtr bo'yicha kinolar topilmadi.",
        "ru": "😔 Фильмы по данному фильтру не найдены.",
        "en": "😔 No movies found for this filter.",
    },
    "filter_results": {
        "uz": "🎛 Filtrlash natijalari: <b>$count</b> ta kino",
        "ru": "🎛 Результаты фильтра: <b>$count</b> фильмов",
        "en": "🎛 Filter results: <b>$count</b> movie(s)",
    },

    # ── MOVIE CARD ─────────────────────────────────────────────────────────
    "movie_not_found": {
        "uz": "❌ Kino topilmadi.",
        "ru": "❌ Фильм не найден.",
        "en": "❌ Movie not found.",
    },
    "movie_blocked": {
        "uz": "⛔ Bu kino hozircha mavjud emas.",
        "ru": "⛔ Этот фильм временно недоступен.",
        "en": "⛔ This movie is currently unavailable.",
    },

    # ── TOP MOVIES ──────────────────────────────────────────────────────────
    "top_choose_period": {
        "uz": "⭐ <b>Top kinolar</b>\n\nDavrni tanlang:",
        "ru": "⭐ <b>Топ фильмов</b>\n\nВыберите период:",
        "en": "⭐ <b>Top Movies</b>\n\nChoose period:",
    },
    "top_choose_count": {
        "uz": "Nechtasini ko'rmoqchisiz?",
        "ru": "Сколько фильмов показать?",
        "en": "How many movies to show?",
    },
    "top_header": {
        "uz": "🏆 <b>Top $count — $period</b>\n\n",
        "ru": "🏆 <b>Топ $count — $period</b>\n\n",
        "en": "🏆 <b>Top $count — $period</b>\n\n",
    },
    "period_weekly":  {"uz": "Haftalik",   "ru": "Еженедельный", "en": "Weekly"},
    "period_monthly": {"uz": "Oylik",      "ru": "Ежемесячный",  "en": "Monthly"},
    "period_yearly":  {"uz": "Yillik",     "ru": "Ежегодный",    "en": "Yearly"},
    "period_alltime": {"uz": "Barcha vaqt","ru": "За всё время", "en": "All Time"},

    # ── RECENT ─────────────────────────────────────────────────────────────
    "recent_header": {
        "uz": "🆕 <b>Oxirgi qo'shilgan kinolar:</b>",
        "ru": "🆕 <b>Последние добавленные фильмы:</b>",
        "en": "🆕 <b>Recently Added Movies:</b>",
    },

    # ── FAVOURITES ──────────────────────────────────────────────────────────
    "favorites_empty": {
        "uz": "❤️ Sevimlilar ro'yxatingiz bo'sh.\n\nKinolarni ❤️ tugmasi bilan saqlang!",
        "ru": "❤️ Ваш список избранного пуст.\n\nСохраняйте фильмы кнопкой ❤️!",
        "en": "❤️ Your favourites list is empty.\n\nSave movies with the ❤️ button!",
    },
    "favorites_header": {
        "uz": "❤️ <b>Sevimlilar — $count ta kino</b>",
        "ru": "❤️ <b>Избранное — $count фильмов</b>",
        "en": "❤️ <b>Favourites — $count movie(s)</b>",
    },
    "favorite_added": {
        "uz": "❤️ Sevimlilar ro'yxatiga qo'shildi!",
        "ru": "❤️ Добавлено в избранное!",
        "en": "❤️ Added to favourites!",
    },
    "favorite_removed": {
        "uz": "💔 Sevimlilar ro'yxatidan o'chirildi.",
        "ru": "💔 Удалено из избранного.",
        "en": "💔 Removed from favourites.",
    },
    "favorite_already": {
        "uz": "ℹ️ Bu kino allaqachon sevimlilar ro'yxatida.",
        "ru": "ℹ️ Этот фильм уже в избранном.",
        "en": "ℹ️ This movie is already in your favourites.",
    },

    # ── WATCH HISTORY ──────────────────────────────────────────────────────
    "history_empty": {
        "uz": "📜 Ko'rish tarixingiz bo'sh.",
        "ru": "📜 История просмотров пуста.",
        "en": "📜 Your watch history is empty.",
    },
    "history_header": {
        "uz": "📜 <b>Ko'rish tarixi — $count ta kino</b>",
        "ru": "📜 <b>История просмотров — $count фильмов</b>",
        "en": "📜 <b>Watch History — $count movie(s)</b>",
    },

    # ── USER MANAGEMENT ────────────────────────────────────────────────────
    "user_blocked": {
        "uz": "⛔ Siz bloklandingiz. Sabab: $reason",
        "ru": "⛔ Вы заблокированы. Причина: $reason",
        "en": "⛔ You have been blocked. Reason: $reason",
    },
    "user_muted": {
        "uz": "🔇 Siz vaqtincha muzlatildingiz.",
        "ru": "🔇 Вы временно заглушены.",
        "en": "🔇 You have been muted temporarily.",
    },
    "user_banned": {
        "uz": "🚫 Siz doimiy ban oldingiz. Sabab: $reason",
        "ru": "🚫 Вы перманентно заблокированы. Причина: $reason",
        "en": "🚫 You have been permanently banned. Reason: $reason",
    },
    "user_temp_banned": {
        "uz": "⏳ Siz $until gacha ban oldingiz.",
        "ru": "⏳ Вы забанены до $until.",
        "en": "⏳ You are banned until $until.",
    },

    # ── BROADCAST ──────────────────────────────────────────────────────────
    "broadcast_received": {
        "uz": "📢 <b>Admin xabari:</b>\n\n$text",
        "ru": "📢 <b>Сообщение от администратора:</b>\n\n$text",
        "en": "📢 <b>Message from admin:</b>\n\n$text",
    },

    # ── ADMIN NOTIFICATIONS ────────────────────────────────────────────────
    "notify_new_user": {
        "uz": "👤 Yangi foydalanuvchi: <b>$name</b> (ID: <code>$id</code>)\n🌍 Til: $lang",
        "ru": "👤 Новый пользователь: <b>$name</b> (ID: <code>$id</code>)\n🌍 Язык: $lang",
        "en": "👤 New user: <b>$name</b> (ID: <code>$id</code>)\n🌍 Language: $lang",
    },
    "notify_new_movie": {
        "uz": "🎬 Yangi kino qo'shildi: <b>$title</b> (Kod: <code>$code</code>)",
        "ru": "🎬 Добавлен новый фильм: <b>$title</b> (Код: <code>$code</code>)",
        "en": "🎬 New movie added: <b>$title</b> (Code: <code>$code</code>)",
    },
    "notify_broadcast_done": {
        "uz": "📢 Broadcast tugadi!\n✅ Yuborildi: $sent\n❌ Xato: $failed",
        "ru": "📢 Рассылка завершена!\n✅ Отправлено: $sent\n❌ Ошибок: $failed",
        "en": "📢 Broadcast finished!\n✅ Sent: $sent\n❌ Failed: $failed",
    },
    "notify_server_error": {
        "uz": "🚨 Server xatosi:\n<code>$error</code>",
        "ru": "🚨 Ошибка сервера:\n<code>$error</code>",
        "en": "🚨 Server error:\n<code>$error</code>",
    },

    # ── CHANNEL GUARD ──────────────────────────────────────────────────────
    "must_subscribe": {
        "uz": (
            "📢 Botdan foydalanish uchun kanalga obuna bo'lish kerak:\n"
            "$channel\n\n"
            "Obuna bo'lgach «✅ Tekshirish» tugmasini bosing."
        ),
        "ru": (
            "📢 Для использования бота необходимо подписаться на канал:\n"
            "$channel\n\n"
            "После подписки нажмите «✅ Проверить»."
        ),
        "en": (
            "📢 To use the bot you must subscribe to the channel:\n"
            "$channel\n\n"
            "After subscribing click «✅ Check»."
        ),
    },
    "btn_check_sub": {
        "uz": "✅ Tekshirish",
        "ru": "✅ Проверить",
        "en": "✅ Check",
    },
    "not_subscribed": {
        "uz": "❌ Obuna topilmadi. Iltimos, avval obuna bo'ling.",
        "ru": "❌ Подписка не найдена. Пожалуйста, сначала подпишитесь.",
        "en": "❌ Subscription not found. Please subscribe first.",
    },

    # ── ERRORS / GENERIC ───────────────────────────────────────────────────
    "error_generic": {
        "uz": "❗ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.",
        "ru": "❗ Произошла ошибка. Пожалуйста, попробуйте позже.",
        "en": "❗ An error occurred. Please try again later.",
    },
    "cancelled": {
        "uz": "❌ Bekor qilindi.",
        "ru": "❌ Отменено.",
        "en": "❌ Cancelled.",
    },
    "coming_soon": {
        "uz": "🚧 Tez orada...",
        "ru": "🚧 Скоро...",
        "en": "🚧 Coming soon...",
    },

    # ── ABOUT ──────────────────────────────────────────────────────────────
    "about": {
        "uz": (
            "🎬 <b>Kino Bot Enterprise</b>\n\n"
            "🏗 Versiya: 2.0.0\n"
            "🛠 Texnologiya: Python · aiogram 3 · PostgreSQL · Redis · FastAPI\n"
            "👨‍💻 Yaratuvchi: @MamurovSH\n\n"
            "📊 Statistika:\n"
            "  🎬 Kinolar: <b>$movies</b> ta\n"
            "  👤 Foydalanuvchilar: <b>$users</b> ta\n\n"
            "❓ Yordam uchun: @MamurovSH"
        ),
        "ru": (
            "🎬 <b>Kino Bot Enterprise</b>\n\n"
            "🏗 Версия: 2.0.0\n"
            "🛠 Технологии: Python · aiogram 3 · PostgreSQL · Redis · FastAPI\n"
            "👨‍💻 Разработчик: @MamurovSH\n\n"
            "📊 Статистика:\n"
            "  🎬 Фильмов: <b>$movies</b>\n"
            "  👤 Пользователей: <b>$users</b>\n\n"
            "❓ По вопросам: @MamurovSH"
        ),
        "en": (
            "🎬 <b>Kino Bot Enterprise</b>\n\n"
            "🏗 Version: 2.0.0\n"
            "🛠 Stack: Python · aiogram 3 · PostgreSQL · Redis · FastAPI\n"
            "👨‍💻 Author: @MamurovSH\n\n"
            "📊 Statistics:\n"
            "  🎬 Movies: <b>$movies</b>\n"
            "  👤 Users: <b>$users</b>\n\n"
            "❓ Support: @MamurovSH"
        ),
    },

    # ── SETTINGS ───────────────────────────────────────────────────────────
    "settings_header": {
        "uz": "⚙️ <b>Sozlamalar</b>\n\nJoriy til: <b>$lang</b>",
        "ru": "⚙️ <b>Настройки</b>\n\nТекущий язык: <b>$lang</b>",
        "en": "⚙️ <b>Settings</b>\n\nCurrent language: <b>$lang</b>",
    },
    "btn_change_lang": {
        "uz": "🌍 Tilni o'zgartirish",
        "ru": "🌍 Изменить язык",
        "en": "🌍 Change Language",
    },
}

_LANG_NAMES = {"uz": "O'zbekcha 🇺🇿", "ru": "Русский 🇷🇺", "en": "English 🇺🇸"}


def t(key: str, lang: str = "uz", **kwargs: Any) -> str:
    """
    Translate a key to the given language, substituting $variable placeholders.
    Falls back to Uzbek, then the raw key if missing.
    """
    lang = lang if lang in ("uz", "ru", "en") else "uz"
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang) or entry.get("uz") or key
    if kwargs:
        try:
            text = Template(text).safe_substitute(kwargs)
        except Exception:
            pass
    return text


def lang_name(lang: str) -> str:
    return _LANG_NAMES.get(lang, lang)
