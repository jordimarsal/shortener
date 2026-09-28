# shortener_app/domain/url.py

from dataclasses import dataclass
from typing import NewType

import validators

from .errors import InvalidTargetUrl
from .keygen import create_random_key

UrlKey = NewType("UrlKey", str)
SecretKey = NewType("SecretKey", str)

SECRET_KEY_SEPARATOR = "_"
SECRET_KEY_SUFFIX_LENGTH = 8
MAX_KEY_GENERATION_ATTEMPTS = 8


@dataclass(frozen=True)
class ShortUrl:
    """A shortened URL. Immutable by design; persistence adapters map it to records."""

    key: UrlKey
    secret_key: SecretKey
    target_url: str
    is_active: bool = True
    clicks: int = 0


def validate_target_url(target_url: str) -> None:
    if not validators.url(target_url):
        raise InvalidTargetUrl(target_url)


def generate_url_key() -> UrlKey:
    return UrlKey(create_random_key())


def compose_secret_key(key: UrlKey, random_suffix: str) -> SecretKey:
    return SecretKey(f"{key}{SECRET_KEY_SEPARATOR}{random_suffix}")


def build_short_url(target_url: str, key: UrlKey) -> ShortUrl:
    # Precondition: the caller has validated target_url and reserved a unique key.
    return ShortUrl(
        key=key,
        secret_key=compose_secret_key(key, create_random_key(length=SECRET_KEY_SUFFIX_LENGTH)),
        target_url=target_url,
    )
