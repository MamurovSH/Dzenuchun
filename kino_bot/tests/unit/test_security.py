"""Unit tests for security module."""
import pytest
from src.core.security import (
    hash_password, verify_password,
    generate_api_key, hash_api_key, verify_api_key,
    sanitise_input,
    generate_2fa_secret, verify_2fa_code,
    create_access_token, decode_token,
)


def test_password_hash_and_verify():
    plain = "MySecureP@ss1"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong", hashed)


def test_api_key_generate_and_verify():
    key = generate_api_key()
    assert key.startswith("kb_")
    hashed = hash_api_key(key)
    assert verify_api_key(key, hashed)
    assert not verify_api_key("wrong_key", hashed)


def test_sanitise_input_strips_tags():
    dirty = "<script>alert('xss')</script>"
    clean = sanitise_input(dirty)
    assert "<" not in clean
    assert ">" not in clean


def test_sanitise_input_max_length():
    long_input = "a" * 1000
    result = sanitise_input(long_input, max_length=100)
    assert len(result) <= 100


def test_jwt_create_and_decode():
    token = create_access_token({"sub": "test_user", "role": "admin"})
    assert token
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user"


def test_jwt_invalid_token():
    payload = decode_token("invalid.token.here")
    assert payload is None


def test_2fa_generate_and_verify():
    secret = generate_2fa_secret()
    assert len(secret) > 10
    import pyotp
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    assert verify_2fa_code(secret, current_code)
    assert not verify_2fa_code(secret, "000000")
