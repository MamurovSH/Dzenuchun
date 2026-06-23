"""
Integration tests for REST API endpoints.
Requires a running PostgreSQL + Redis (use pytest-asyncio).
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.api.app import api_app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=api_app),
        base_url="http://test",
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    resp = await client.get("/health/")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "system" in data


@pytest.mark.asyncio
async def test_health_ping(client: AsyncClient):
    resp = await client.get("/health/ping")
    assert resp.status_code == 200
    assert resp.json()["ping"] == "pong"


@pytest.mark.asyncio
async def test_movies_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/movies/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_search_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/movies/search?q=titanic")
    assert resp.status_code == 401
