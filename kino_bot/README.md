# 🎬 Kino Bot Enterprise v2.0.0

> Production-ready, enterprise-level Telegram movie bot.
> Stack: **Python 3.12 · aiogram 3.x · PostgreSQL · Redis · FastAPI · Docker**

---

## ✨ Features

| Category | Feature |
|---|---|
| 🔍 **Smart Search** | Code, UZ/RU/EN name, partial name, director, tags — cached in Redis |
| 🎛 **Filter Search** | Genre, Year, Country, Language, Rating — paginated results |
| ⭐ **Top Movies** | Weekly / Monthly / Yearly / All-time · Top 10 / 50 / 100 |
| 🆕 **Recent Movies** | Latest added, inline navigation |
| ❤️ **Favorites** | Per-user saved list, add/remove |
| 📜 **Watch History** | Last 1000 views per user |
| 👮 **Multi-Admin** | Super Admin · Admin · Moderator · Support — role-based permissions |
| 📤 **Export** | CSV, Excel, JSON for Movies, Users, Stats |
| 🌍 **Multi-Language** | O'zbekcha 🇺🇿 · Русский 🇷🇺 · English 🇺🇸 (all strings in `src/utils/i18n.py`) |
| 🧭 **Inline Navigation** | Back · Next · Prev · Home · Search Again · Share |
| 🚫 **User Management** | Block · Unblock · Mute · Warn · Ban · Temp Ban |
| 📢 **Broadcast** | Scheduled, preview, cancel, retry, per-language targeting, stats |
| 🌐 **REST API** | FastAPI + JWT + API Key + Rate Limit + Swagger (`/docs`) |
| 🏥 **Health Check** | CPU, RAM, Disk, DB, Redis — `/health/` |
| 🎛 **Dashboard** | Bootstrap 5 admin panel with charts — `localhost:8080/dashboard/` |
| 🔴 **Redis Cache** | Search, movie card, top movies, stats — all cached |
| 🔐 **Security** | 2FA (TOTP), JWT, API Key, Helmet-equivalent headers, CORS, Rate Limit, Input Sanitisation |
| 🔔 **Notifications** | New user, new movie, broadcast done, server error → all admins |
| 📊 **Analytics** | Daily snapshots, weekly/monthly/yearly charts |
| 🧹 **Auto Cleanup** | Expired bans/mutes, old logs, stale cache — every 6h |

---

## 🚀 Quick Start

### 1. Clone & configure
```bash
git clone https://github.com/MamurovSH/Dzenuchun.git
cd Dzenuchun/kino_bot
cp .env.example .env
# Edit .env with your BOT_TOKEN, SUPER_ADMIN_ID, etc.
```

### 2. Run with Docker (recommended)
```bash
docker-compose up -d
```

### 3. Seed sample movies
```bash
docker-compose exec bot python scripts/seed_movies.py
```

### 4. Open services
| Service | URL |
|---|---|
| Telegram Bot | Start `@your_bot` |
| REST API + Swagger | http://localhost:8000/docs |
| Admin Dashboard | http://localhost:8080/dashboard/ |
| Health Check | http://localhost:8000/health/ |

---

## 🏃 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (or use Docker)
docker-compose up -d postgres redis

# Run all services
python main.py

# Or run separately
python main.py bot        # Telegram bot only
python main.py api        # REST API only
python main.py dashboard  # Dashboard only
```

---

## 🗄️ Database Migrations

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## 🧪 Tests

```bash
pytest tests/unit/           # Unit tests (no DB required)
pytest tests/integration/    # Integration tests (requires DB + Redis)
pytest --cov=src             # With coverage
```

---

## 🌐 REST API

Authentication: `X-API-Key: kb_<your_key>` header or `Authorization: Bearer <jwt>`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health/` | Health check |
| GET | `/api/v1/movies/` | List movies (paginated) |
| GET | `/api/v1/movies/search?q=titanic` | Smart search |
| GET | `/api/v1/movies/top/{period}` | Top movies |
| POST | `/api/v1/movies/` | Create movie |
| GET | `/api/v1/users/` | List users |
| POST | `/api/v1/users/{id}/block` | Block user |
| GET | `/api/v1/stats/overview` | Bot statistics |
| GET | `/api/v1/broadcasts/` | List broadcasts |

Full Swagger docs: **http://localhost:8000/docs**

---

## 🏗️ Architecture

```
kino_bot/
├── main.py                  # Entry point (bot + api + dashboard)
├── src/
│   ├── core/                # Config, logging, security
│   ├── db/
│   │   ├── models/          # SQLAlchemy models
│   │   └── repositories/    # DB access layer
│   ├── services/            # Business logic (cache, broadcast, analytics, cleanup, export)
│   ├── bot/
│   │   ├── handlers/        # Telegram message/callback handlers
│   │   ├── middlewares/     # User loader, admin auth
│   │   ├── filters/         # IsAdmin, HasPermission
│   │   └── keyboards.py     # All inline/reply keyboards
│   ├── api/                 # FastAPI REST API
│   ├── dashboard/           # Admin web dashboard
│   └── utils/               # i18n, formatters
├── tests/
│   ├── unit/
│   └── integration/
├── scripts/                 # seed_movies.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 👮 Admin Roles

| Role | Permissions |
|---|---|
| **Super Admin** | All permissions including managing other admins and settings |
| **Admin** | Manage movies, users, broadcast, export, view logs |
| **Moderator** | Manage movies & users, view stats and logs |
| **Support** | View users and stats only |

Add admin via bot: `/admin` → Adminlar → ➕ Admin qo'shish

---

## 🔐 Security

- **2FA** (TOTP) for admin login
- **JWT** access + refresh tokens
- **API Key** hashed with SHA-256
- **Rate limiting** via Redis (60 req/min)
- **Input sanitisation** — strips XSS/injection characters
- **CORS** configurable via `CORS_ORIGINS`
- **Non-root Docker** user

---

## 📞 Support

- Author: [@MamurovSH](https://t.me/MamurovSH)
- Issues: [GitHub Issues](https://github.com/MamurovSH/Dzenuchun/issues)
