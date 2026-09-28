# tests/test_keygen.py

import string

from shortener_app.domain.keygen import KEY_ALPHABET, KEY_LENGTH, create_random_key


def test_create_random_key_uses_default_length() -> None:
    assert len(create_random_key()) == KEY_LENGTH


def test_create_random_key_honors_custom_length() -> None:
    assert len(create_random_key(length=12)) == 12


def test_create_random_key_only_uses_uppercase_letters_and_digits() -> None:
    assert string.ascii_uppercase + string.digits == KEY_ALPHABET
    key = create_random_key(length=64)
    assert all(char in KEY_ALPHABET for char in key)


def test_create_random_key_generates_distinct_keys() -> None:
    keys = {create_random_key(length=16) for _ in range(32)}
    assert len(keys) == 32
