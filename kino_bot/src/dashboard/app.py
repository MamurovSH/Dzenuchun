"""
Admin Dashboard — FastAPI + Jinja2 templates (#18).
Shows live charts: daily users, daily movies, searches, broadcasts.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import settings
from src.core.security import verify_password
from src.db.base import AsyncSessionFactory
from src.db.repositories.analytics_repo import AnalyticsRepository
from src.db.repositories.broadcast_repo import BroadcastRepository
from src.db.repositories.movie_repo import MovieRepository
from src.db.repositories.user_repo import UserRepository
from src.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)

BASE = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE / "templates"))


def create_dashboard_app() -> FastAPI:
    app = FastAPI(
        title="Kino Bot Dashboard",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(SessionMiddleware, secret_key=settings.dashboard_secret_key)

    static_dir = BASE / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # ── Auth helpers ───────────────────────────────────────────────────────

    def is_logged_in(request: Request) -> bool:
        return request.session.get("admin_logged_in", False)

    def require_login(request: Request):
        if not is_logged_in(request):
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/dashboard/login"},
            )

    # ── Routes ─────────────────────────────────────────────────────────────

    @app.get("/", response_class=RedirectResponse)
    async def root():
        return RedirectResponse(url="/dashboard/")

    @app.get("/dashboard/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request, "error": None})

    @app.post("/dashboard/login", response_class=HTMLResponse)
    async def login_submit(request: Request):
        form = await request.form()
        password = form.get("password", "")
        # Simple password check against dashboard secret key
        if password == settings.dashboard_secret_key:
            request.session["admin_logged_in"] = True
            return RedirectResponse(url="/dashboard/", status_code=303)
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid password"})

    @app.get("/dashboard/logout")
    async def logout(request: Request):
        request.session.clear()
        return RedirectResponse(url="/dashboard/login")

    @app.get("/dashboard/", response_class=HTMLResponse)
    async def dashboard_home(request: Request):
        require_login(request)
        service = AnalyticsService()
        overview = await service.get_overview()
        weekly = await service.get_period_stats("weekly")

        async with AsyncSessionFactory() as session:
            movie_count = await MovieRepository(session).count_total()
            user_count = await UserRepository(session).count_total()
            active_today = await UserRepository(session).count_active_today()
            broadcasts = await BroadcastRepository(session).list_all(limit=5)

        chart_labels = [s["date"] for s in weekly]
        chart_users = [s["active_users"] for s in weekly]
        chart_views = [s["total_views"] for s in weekly]
        chart_searches = [s["total_searches"] for s in weekly]

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "movie_count": movie_count,
            "user_count": user_count,
            "active_today": active_today,
            "broadcasts": broadcasts,
            "chart_labels": json.dumps(chart_labels),
            "chart_users": json.dumps(chart_users),
            "chart_views": json.dumps(chart_views),
            "chart_searches": json.dumps(chart_searches),
        })

    @app.get("/dashboard/movies", response_class=HTMLResponse)
    async def dashboard_movies(request: Request, page: int = 0):
        require_login(request)
        async with AsyncSessionFactory() as session:
            movies, total = await MovieRepository(session).get_all(page=page, per_page=20)
        return templates.TemplateResponse("movies.html", {
            "request": request,
            "movies": movies,
            "total": total,
            "page": page,
            "pages": max(1, (total + 19) // 20),
        })

    @app.get("/dashboard/users", response_class=HTMLResponse)
    async def dashboard_users(request: Request, page: int = 0):
        require_login(request)
        async with AsyncSessionFactory() as session:
            users, total = await UserRepository(session).get_page(page=page, per_page=20)
        return templates.TemplateResponse("users.html", {
            "request": request,
            "users": users,
            "total": total,
            "page": page,
            "pages": max(1, (total + 19) // 20),
        })

    return app


dashboard_app = create_dashboard_app()
