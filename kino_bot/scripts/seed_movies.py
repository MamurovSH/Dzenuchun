"""
Seed script — migrates old data/movies.py into PostgreSQL.
Usage: python scripts/seed_movies.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.base import AsyncSessionFactory, create_all_tables
from src.db.repositories.movie_repo import MovieRepository

SEED_MOVIES = [
    {
        "code": "INT001", "title": "Интерстеллар",
        "title_uz": "Interstellar", "title_ru": "Интерстеллар", "title_en": "Interstellar",
        "year": 2014, "genres": ["Fantastika", "Drama", "Sarguzasht"],
        "director": "Kristofer Nolan", "rating": 8.7, "country": "AQSh",
        "language": "Inglizcha", "duration": "169 daqiqa",
        "description_uz": "Insoniyatni qutqarish uchun bir guruh tadqiqotchilar kosmosga uchadi.",
        "watch_url": "https://www.kinopoisk.ru/film/258687/",
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "tags": ["kosmik", "vaqt", "oila", "ilmiy"],
    },
    {
        "code": "INC001", "title": "Начало",
        "title_uz": "Boshliq (Inception)", "title_ru": "Начало", "title_en": "Inception",
        "year": 2010, "genres": ["Triller", "Fantastika", "Sarguzasht"],
        "director": "Kristofer Nolan", "rating": 8.8, "country": "AQSh",
        "language": "Inglizcha", "duration": "148 daqiqa",
        "description_uz": "Dom Kobb ong osti orzularga kirish va g'oyalarni o'g'irlash ustasi.",
        "watch_url": "https://www.kinopoisk.ru/film/447301/",
        "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
        "tags": ["orzu", "psixologik", "aql"],
    },
    {
        "code": "SHA001", "title": "Побег из Шоушенка",
        "title_uz": "Shoushenk qochishi", "title_ru": "Побег из Шоушенка", "title_en": "The Shawshank Redemption",
        "year": 1994, "genres": ["Drama"],
        "director": "Frenk Darabont", "rating": 9.3, "country": "AQSh",
        "language": "Inglizcha", "duration": "142 daqiqa",
        "description_uz": "Nohaq qamalgan Andy Dufresne qamoqxonada umid va do'stlik orqali ozodlikka intiladi.",
        "watch_url": "https://www.kinopoisk.ru/film/326/",
        "trailer_url": "https://www.youtube.com/watch?v=6hB3S9bIaco",
        "tags": ["qamoq", "ozodlik", "do'stlik", "umid"],
    },
    {
        "code": "GRM001", "title": "Зеленая миля",
        "title_uz": "Yashil mayl", "title_ru": "Зелёная миля", "title_en": "The Green Mile",
        "year": 1999, "genres": ["Drama", "Fantastika", "Mistika"],
        "director": "Frenk Darabont", "rating": 8.6, "country": "AQSh",
        "language": "Inglizcha", "duration": "189 daqiqa",
        "description_uz": "O'lim jazosi qamoqxonasida g'ayritabiiy kuchlarga ega mahkum paydo bo'ladi.",
        "watch_url": "https://www.kinopoisk.ru/film/435/",
        "trailer_url": "https://www.youtube.com/watch?v=Ki4haFrqSrw",
        "tags": ["mo'jiza", "dramatik", "his-tuyg'u"],
    },
    {
        "code": "TIT001", "title": "Титаник",
        "title_uz": "Titanik", "title_ru": "Титаник", "title_en": "Titanic",
        "year": 1997, "genres": ["Drama", "Romantika"],
        "director": "Jeyms Kameron", "rating": 7.9, "country": "AQSh",
        "language": "Inglizcha", "duration": "194 daqiqa",
        "description_uz": "Jack va Rose ning Titanik kemasi cho'kib ketayotganda sevgisi.",
        "watch_url": "https://www.kinopoisk.ru/film/344/",
        "trailer_url": "https://www.youtube.com/watch?v=kVrqfYjkTdQ",
        "tags": ["muhabbat", "falokat", "dengiz", "romantika"],
    },
    {
        "code": "DKN001", "title": "Темный рыцарь",
        "title_uz": "Qorong'u ritsar", "title_ru": "Тёмный рыцарь", "title_en": "The Dark Knight",
        "year": 2008, "genres": ["Boevik", "Triller", "Drama"],
        "director": "Kristofer Nolan", "rating": 9.0, "country": "AQSh",
        "language": "Inglizcha", "duration": "152 daqiqa",
        "description_uz": "Batman Gotam shahrini Joker terroridan himoya qiladi.",
        "watch_url": "https://www.kinopoisk.ru/film/404900/",
        "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
        "tags": ["batman", "superqahramon", "jinoyat"],
    },
    {
        "code": "GOD001", "title": "Крёстный отец",
        "title_uz": "Cho'qintirgan ota", "title_ru": "Крёстный отец", "title_en": "The Godfather",
        "year": 1972, "genres": ["Drama", "Jinoyat"],
        "director": "Frensis Ford Koppola", "rating": 9.2, "country": "AQSh",
        "language": "Inglizcha", "duration": "175 daqiqa",
        "description_uz": "Italyan mafia oilasi Korleone ning hayoti va meros kurashi.",
        "watch_url": "https://www.kinopoisk.ru/film/341/",
        "trailer_url": "https://www.youtube.com/watch?v=sY1S34973zA",
        "tags": ["mafia", "oila", "kuch", "klassik"],
    },
    {
        "code": "FOR001", "title": "Форрест Гамп",
        "title_uz": "Forrest Gamp", "title_ru": "Форрест Гамп", "title_en": "Forrest Gump",
        "year": 1994, "genres": ["Drama", "Komediya", "Romantika"],
        "director": "Robert Zemekis", "rating": 8.8, "country": "AQSh",
        "language": "Inglizcha", "duration": "142 daqiqa",
        "description_uz": "Forrest Gamp tasodifan Amerika tarixining eng muhim voqealarida ishtirok etadi.",
        "watch_url": "https://www.kinopoisk.ru/film/448/",
        "trailer_url": "https://www.youtube.com/watch?v=bLvqoHBptjg",
        "tags": ["ilhom", "hayot", "muhabbat", "sport"],
    },
    {
        "code": "AVG001", "title": "Мстители",
        "title_uz": "Qasoskorlar", "title_ru": "Мстители", "title_en": "The Avengers",
        "year": 2012, "genres": ["Boevik", "Fantastika", "Sarguzasht"],
        "director": "Joss Whedon", "rating": 8.0, "country": "AQSh",
        "language": "Inglizcha", "duration": "143 daqiqa",
        "description_uz": "Super qahramonlar yer yuzini qutqarish uchun birlashadi.",
        "watch_url": "https://www.kinopoisk.ru/film/263531/",
        "trailer_url": "https://www.youtube.com/watch?v=eOrNdBpGMv8",
        "tags": ["superqahramon", "marvel", "boevik"],
    },
    {
        "code": "HAR001", "title": "Гарри Поттер",
        "title_uz": "Garri Potter va Sehr Toshi", "title_ru": "Гарри Поттер и философский камень", "title_en": "Harry Potter and the Sorcerer's Stone",
        "year": 2001, "genres": ["Fantaziya", "Sarguzasht"],
        "director": "Kris Kolumbus", "rating": 7.6, "country": "Buyuk Britaniya",
        "language": "Inglizcha", "duration": "152 daqiqa",
        "description_uz": "Garri Potter sehr dunyosiga qadam qo'yadi.",
        "watch_url": "https://www.kinopoisk.ru/film/689/",
        "trailer_url": "https://www.youtube.com/watch?v=VyHV0BRtdxo",
        "tags": ["sehrgar", "maktab", "fantaziya", "bolalar"],
    },
]


async def seed():
    await create_all_tables()
    async with AsyncSessionFactory() as session:
        repo = MovieRepository(session)
        seeded = 0
        for data in SEED_MOVIES:
            existing = await repo.get_by_code(data["code"])
            if not existing:
                await repo.create(**data)
                seeded += 1
                print(f"  ✅ Added: {data['code']} — {data['title_en']}")
            else:
                print(f"  ⏭  Skip (exists): {data['code']}")
        await session.commit()
    print(f"\n🎬 Seeding complete: {seeded} movies added")


if __name__ == "__main__":
    asyncio.run(seed())
