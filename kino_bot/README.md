# 🎬 Kino Bot — Telegram Film Katalogi

Telegram orqali filmlar qidirish, janr va reyting bo'yicha saralash botı.

---

## ✨ Xususiyatlar

| Funksiya | Tavsif |
|---|---|
| 🎬 Katalog | Barcha filmlar ro'yxati (sahifalash bilan) |
| 🔍 Qidirish | Nom, rejissyor, kalit so'z bo'yicha |
| 🎭 Janr | 17 ta janr bo'yicha saralash |
| ⭐ Top filmlar | Eng yuqori reytingli 5 ta film |
| 🎲 Tasodifiy | Har safar yangi tavsiya |
| ▶️ Tomosha | KinoPoisk + YouTube treyler havolalari |

---

## 🚀 Ishga tushirish

### 1. Tokenni oling
1. Telegramda [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `MyMovieBot`)
4. Username kiriting (masalan: `my_movie_bot`)
5. **Token**ni nusxa oling

### 2. Admin ID ni toping
[@userinfobot](https://t.me/userinfobot) ga `/start` yuboring — ID ingiz ko'rinadi

### 3. O'rnatish

```bash
# Repozitoriyani yuklab oling
git clone https://github.com/MamurovSH/Dzenuchun.git
cd Dzenuchun/kino_bot

# Virtual muhit yarating
python -m venv venv
source venv/bin/activate        # Linux/Mac
# yoki
venv\Scripts\activate           # Windows

# Kutubxonalarni o'rnating
pip install -r requirements.txt

# .env faylini yarating
cp .env.example .env
```

### 4. .env faylini to'ldiring

```env
BOT_TOKEN=1234567890:AABBCCDDEEFFaabbccddeeff
ADMIN_ID=123456789
```

### 5. Botni ishga tushiring

```bash
python bot.py
```

---

## 📁 Fayl tuzilmasi

```
kino_bot/
├── bot.py              # Asosiy bot kodi
├── config.py           # Sozlamalar
├── keyboards.py        # Inline va Reply klaviaturalar
├── requirements.txt    # Python kutubxonalari
├── .env.example        # .env namuna
├── .gitignore
├── README.md
└── data/
    ├── __init__.py
    └── movies.py       # Filmlar ma'lumotlar bazasi
```

---

## 🎬 Film qo'shish

`data/movies.py` faylini oching va `MOVIES` ro'yxatiga yangi film qo'shing:

```python
{
    "id": 11,                          # Unikal ID
    "title": "Rus nomi",
    "title_uz": "O'zbek nomi",
    "year": 2023,
    "genre": ["Drama", "Triller"],
    "director": "Rejissyor ismi",
    "rating": 8.5,                     # 0.0 — 10.0
    "description": "Qisqacha tavsif",
    "duration": "120 daqiqa",
    "country": "Mamlakat",
    "language": "Til",
    "poster": "https://poster_url",
    "watch_url": "https://kinopoisk.ru/...",
    "trailer_url": "https://youtube.com/...",
    "tags": ["kalit", "so'zlar"],
}
```

---

## 🤖 Bot buyruqlari

```
/start   — Botni ishga tushirish
/catalog — Filmlar katalogi
/top     — Top 5 film
/random  — Tasodifiy film
/search  — Qidirish
/help    — Yordam
/stats   — Statistika (faqat admin)
```

---

## 👨‍💻 Yaratuvchi

**@MamurovSH** — [GitHub](https://github.com/MamurovSH)

---

## 📜 Litsenziya

MIT License
