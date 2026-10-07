# shortener_app/ports/url_repository.py

from collections.abc import Awaitable
from typing import Protocol

from ..domain.url import SecretKey, ShortUrl, UrlKey


class UrlRepository(Protocol):
    """Outbound port for short URL persistence. Adapters implement the CRUD I/O.

    Methods return Awaitable so async-native adapters (SQLAlchemy async) and the
    in-memory test fakes satisfy the same protocol.
    """

    def add(self, url: ShortUrl) -> Awaitable[ShortUrl]:
        """Persist a new short URL and return it."""
        ...

    def find_by_key(self, key: UrlKey) -> Awaitable[ShortUrl | None]:
        """Return the active short URL with this key, or None."""
        ...

    def find_by_secret_key(self, secret_key: SecretKey) -> Awaitable[ShortUrl | None]:
        """Return the active short URL with this secret key, or None."""
        ...

    def record_click(self, key: UrlKey) -> Awaitable[None]:
        """Atomically increment the click counter of the active URL with this key."""
        ...

    def deactivate(self, secret_key: SecretKey) -> Awaitable[ShortUrl | None]:
        """Deactivate the active short URL with this secret key; return it, or None if absent."""
        ...
