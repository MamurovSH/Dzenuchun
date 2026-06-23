"""Unit tests for i18n module."""
import pytest
from src.utils.i18n import t, lang_name


def test_translate_existing_key():
    text = t("welcome", "uz", name="Ali")
    assert "Ali" in text
    assert "Kino Bot" in text


def test_translate_russian():
    text = t("welcome", "ru", name="Aleks")
    assert "Aleks" in text


def test_translate_english():
    text = t("welcome", "en", name="John")
    assert "John" in text


def test_translate_missing_key():
    result = t("nonexistent_key_xyz", "uz")
    assert result == "nonexistent_key_xyz"


def test_translate_fallback_to_uz():
    # If only uz exists, ru should fall back to uz
    text = t("btn_home", "ru")
    assert text  # Should not be empty


def test_lang_name():
    assert "O'zbekcha" in lang_name("uz")
    assert "Русский" in lang_name("ru")
    assert "English" in lang_name("en")


def test_template_substitution():
    text = t("search_results", "uz", query="Titanic", count=5)
    assert "Titanic" in text
    assert "5" in text


def test_invalid_lang_falls_back():
    text = t("btn_home", "de")  # German not supported
    assert text  # Should still return uz fallback
