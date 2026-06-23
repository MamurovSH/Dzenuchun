"""Unit tests for formatters module."""
import pytest
from unittest.mock import MagicMock
from src.utils.formatters import format_movie_card, format_user_info, format_stats


def _make_movie(**kwargs):
    m = MagicMock()
    m.code = kwargs.get("code", "TST001")
    m.title = kwargs.get("title", "Test Movie")
    m.title_uz = kwargs.get("title_uz", "Test Kino")
    m.title_ru = kwargs.get("title_ru", None)
    m.title_en = kwargs.get("title_en", "Test Movie EN")
    m.year = kwargs.get("year", 2023)
    m.genres = kwargs.get("genres", ["Drama"])
    m.director = kwargs.get("director", "Test Director")
    m.duration = kwargs.get("duration", "120 min")
    m.country = kwargs.get("country", "USA")
    m.language = kwargs.get("language", "English")
    m.rating = kwargs.get("rating", 8.5)
    m.view_count = kwargs.get("view_count", 1000)
    m.tags = kwargs.get("tags", ["drama", "test"])
    m.watch_url = kwargs.get("watch_url", "https://example.com")
    m.trailer_url = kwargs.get("trailer_url", "https://example.com/trailer")
    m.poster_url = kwargs.get("poster_url", None)
    m.get_title.return_value = m.title_uz or m.title
    m.get_description.return_value = "Test description"
    return m


def test_format_movie_card_contains_key_fields():
    movie = _make_movie()
    card = format_movie_card(movie, "uz")
    assert "TST001" in card
    assert "2023" in card
    assert "8.5" in card
    assert "Drama" in card


def test_format_movie_card_shows_views():
    movie = _make_movie(view_count=12345)
    card = format_movie_card(movie, "uz")
    assert "12,345" in card


def test_format_stats():
    stats = {"total_movies": 100, "total_users": 500, "active_today": 42, "total_searches": 999, "total_views": 5000}
    text = format_stats(stats)
    assert "100" in text
    assert "500" in text
    assert "42" in text
