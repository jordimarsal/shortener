# shortener_app/domain/keygen.py

import secrets
import string

KEY_LENGTH = 5
KEY_ALPHABET = string.ascii_uppercase + string.digits


def create_random_key(length: int = KEY_LENGTH) -> str:
    return "".join(secrets.choice(KEY_ALPHABET) for _ in range(length))
