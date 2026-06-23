# ============================================================
# FILMLAR MA'LUMOTLAR BAZASI
# Yangi film qo'shish uchun shu ro'yxatga qo'shing
# ============================================================

MOVIES = [
    {
        "id": 1,
        "title": "Интерстеллар",
        "title_uz": "Interstellar",
        "year": 2014,
        "genre": ["Fantastika", "Drama", "Sarguzasht"],
        "director": "Kristofer Nolan",
        "rating": 8.7,
        "description": (
            "Insoniyatni qutqarish uchun bir guruh tadqiqotchilar "
            "kosmosga uchib, yulduzlararo sayohat qilishadi. "
            "Vaqt va gravitatsiya sirlari ochiladi."
        ),
        "duration": "169 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BZjdkOTU3MDktN2IxOS00OGEyLWFmMjktY2FiMmZkNWIyODZiXkEyXkFqcGdeQXVyMTMxODk2OTU@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/258687/",
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "tags": ["kosmik", "vaqt", "oila", "ilmiy"],
    },
    {
        "id": 2,
        "title": "Начало",
        "title_uz": "Boshliq (Inception)",
        "year": 2010,
        "genre": ["Triller", "Fantastika", "Sarguzasht"],
        "director": "Kristofer Nolan",
        "rating": 8.8,
        "description": (
            "Dom Kobb ong osti orzularga kirish va g'oyalarni o'g'irlash "
            "ustasi. Ammo unga endi aksincha — g'oyani kiritish vazifasi topshiriladi."
        ),
        "duration": "148 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/447301/",
        "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
        "tags": ["orzu", "psixologik", "aql"],
    },
    {
        "id": 3,
        "title": "Побег из Шоушенка",
        "title_uz": "Shoushenk qochishi",
        "year": 1994,
        "genre": ["Drama"],
        "director": "Frenk Darabont",
        "rating": 9.3,
        "description": (
            "Nohaq qamalgan Andy Dufresne qamoqxonada umid va do'stlik "
            "orqali ozodlikka intiladi. Barcha zamonlarning eng yaxshi filmi."
        ),
        "duration": "142 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BNDE3ODcxYzMtY2YzZC00NiYyLTg3YzItOTEwYjlkMjBlMmU4XkEyXkFqcGdeQXVyNjAwNDUxODI@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/326/",
        "trailer_url": "https://www.youtube.com/watch?v=6hB3S9bIaco",
        "tags": ["qamoq", "ozodlik", "do'stlik", "umid"],
    },
    {
        "id": 4,
        "title": "Зеленая миля",
        "title_uz": "Yashil mayl",
        "year": 1999,
        "genre": ["Drama", "Fantastika", "Mistika"],
        "director": "Frenk Darabont",
        "rating": 8.6,
        "description": (
            "O'lim jazosi qamoqxonasida g'ayritabiiy kuchlarga ega "
            "mahkum John Coffey paydo bo'ladi. U odamlarni davolay oladi."
        ),
        "duration": "189 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BMTUxMzQyNjA5MF5BMl5BanBnXkFtZTYwOTU2NTY3._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/435/",
        "trailer_url": "https://www.youtube.com/watch?v=Ki4haFrqSrw",
        "tags": ["mo'jiza", "dramatik", "his-tuyg'u"],
    },
    {
        "id": 5,
        "title": "Властелин колец: Братство кольца",
        "title_uz": "Uzuklar hukmdori: Uzuk birodarlighi",
        "year": 2001,
        "genre": ["Fantaziya", "Sarguzasht", "Drama"],
        "director": "Piter Jekson",
        "rating": 8.8,
        "description": (
            "Froddo Bagins yovuz kuchni yo'q qilish uchun xavfli safarga "
            "chiqadi. Do'stlar bilan yovuz Sauronni mag'lub etish kerak."
        ),
        "duration": "178 daqiqa",
        "country": "Yangi Zelandiya",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BN2EyZjM3NzUtNWUzMi00MTgxLWI0NTctMzY4M2VlOTdjZWRiXkEyXkFqcGdeQXVyNDUzOTQ5MjY@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/328/",
        "trailer_url": "https://www.youtube.com/watch?v=V75dMMIW2B4",
        "tags": ["fantaziya", "sarguzasht", "epik"],
    },
    {
        "id": 6,
        "title": "Темный рыцарь",
        "title_uz": "Qorong'u ritsar",
        "year": 2008,
        "genre": ["Boevik", "Triller", "Drama"],
        "director": "Kristofer Nolan",
        "rating": 9.0,
        "description": (
            "Batman Gotam shahrini Joker degan aqldan ozgan jinoyatchi "
            "terroridan himoya qiladi. Yaxshilik va yomonlik o'rtasidagi kurash."
        ),
        "duration": "152 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/404900/",
        "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
        "tags": ["batman", "superqahramon", "jinoyat"],
    },
    {
        "id": 7,
        "title": "Список Шиндлера",
        "title_uz": "Shindler ro'yxati",
        "year": 1993,
        "genre": ["Drama", "Tarix", "Urush"],
        "director": "Stiven Spilberg",
        "rating": 9.0,
        "description": (
            "Nemis ishbilarmon Oskar Shindler ikkinchi jahon urushi paytida "
            "minglab yahudiy hayotini qutqaradi. Haqiqiy voqeaga asoslangan."
        ),
        "duration": "195 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha / Nemischa",
        "poster": "https://m.media-amazon.com/images/M/MV5BNDE4OTEyMDQtOTY5NS00Y2RjLWE4NGUtZWViYWI2ZmZlMDZhXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/329/",
        "trailer_url": "https://www.youtube.com/watch?v=gG22XNhtnoY",
        "tags": ["urush", "tarix", "insonparvarlik"],
    },
    {
        "id": 8,
        "title": "Форрест Гамп",
        "title_uz": "Forrest Gamp",
        "year": 1994,
        "genre": ["Drama", "Komediya", "Romantika"],
        "director": "Robert Zemekis",
        "rating": 8.8,
        "description": (
            "Past aql-idrokli Forrest Gamp tasodifan Amerika tarixining "
            "eng muhim voqealarida ishtirok etadi va hech qachon umidini yo'qotmaydi."
        ),
        "duration": "142 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BNWIwODRlZTUtY2U3ZS00Yzk1LWJlZDUtNTRhZjdlOWM5NmU3XkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/448/",
        "trailer_url": "https://www.youtube.com/watch?v=bLvqoHBptjg",
        "tags": ["ilhom", "hayot", "muhabbat", "sport"],
    },
    {
        "id": 9,
        "title": "Крёстный отец",
        "title_uz": "Cho'qintirgan ota",
        "year": 1972,
        "genre": ["Drama", "Jinoyat"],
        "director": "Frensis Ford Koppola",
        "rating": 9.2,
        "description": (
            "Italyan mafia oilasi Korleone ning hayoti va meros kurashi. "
            "Barcha zamonlarning eng ulug' filmlaridan biri."
        ),
        "duration": "175 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmUtYTAwNi00MTYxLWJmNWYtYzZlODY3ZTk3OTFlXkEyXkFqcGdeQXVyNzkwMjQ5NzM@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/341/",
        "trailer_url": "https://www.youtube.com/watch?v=sY1S34973zA",
        "tags": ["mafia", "oila", "kuch", "klassik"],
    },
    {
        "id": 10,
        "title": "Титаник",
        "title_uz": "Titanik",
        "year": 1997,
        "genre": ["Drama", "Romantika", "Falokat"],
        "director": "Jeyms Kameron",
        "rating": 7.9,
        "description": (
            "Boylik va kambag'allikning sevgisi — Jack va Rose. "
            "Titanik kemasi cho'kib ketayotganda ularning sevgisi sinovdan o'tadi."
        ),
        "duration": "194 daqiqa",
        "country": "AQSh",
        "language": "Inglizcha",
        "poster": "https://m.media-amazon.com/images/M/MV5BMDdmZGU3NDQtY2E5My00ZTliLWIzOTUtMTY4ZGI1YjdiNjk3XkEyXkFqcGdeQXVyNTA4NzY1MzY@._V1_.jpg",
        "watch_url": "https://www.kinopoisk.ru/film/344/",
        "trailer_url": "https://www.youtube.com/watch?v=kVrqfYjkTdQ",
        "tags": ["muhabbat", "falokat", "dengiz", "romantika"],
    },
]

# Janrlar ro'yxati
GENRES = [
    "Boevik", "Animatsiya", "Biografiya", "Drama",
    "Dokumentali", "Fantastika", "Fantaziya", "Komediya",
    "Jinoyat", "Mistika", "Muzikl", "Romantika",
    "Sarguzasht", "Sport", "Tarix", "Triller", "Urush",
]


def get_all_movies():
    """Barcha filmlarni qaytaradi"""
    return MOVIES


def get_movie_by_id(movie_id: int):
    """ID bo'yicha film topadi"""
    for movie in MOVIES:
        if movie["id"] == movie_id:
            return movie
    return None


def search_movies(query: str):
    """Film nomini qidiradi"""
    query = query.lower()
    results = []
    for movie in MOVIES:
        if (
            query in movie["title"].lower()
            or query in movie["title_uz"].lower()
            or query in movie["director"].lower()
            or any(query in tag for tag in movie["tags"])
        ):
            results.append(movie)
    return results


def get_movies_by_genre(genre: str):
    """Janr bo'yicha filmlarni qaytaradi"""
    return [m for m in MOVIES if genre in m["genre"]]


def get_top_movies(limit: int = 5):
    """Eng yuqori reytingli filmlar"""
    return sorted(MOVIES, key=lambda x: x["rating"], reverse=True)[:limit]
