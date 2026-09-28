# shortener_app/ports/url_repository.py

from typing import Protocol

from ..domain.url import SecretKey, ShortUrl, UrlKey


class UrlRepository(Protocol):
    """Outbound port for short URL persistence. Adapters implement the CRUD I/O."""

    async def add(self, url: ShortUrl) -> ShortUrl:
        """Persist a new short URL and return it."""
        ...

    async def find_by_key(self, key: UrlKey) -> ShortUrl | None:
        """Return the active short URL with this key, or None."""
        ...

    async def find_by_secret_key(self, secret_key: SecretKey) -> ShortUrl | None:
        """Return the active short URL with this secret key, or None."""
        ...

    async def record_click(self, key: UrlKey) -> None:
        """Atomically increment the click counter of the active URL with this key."""
        ...

    async def deactivate(self, secret_key: SecretKey) -> ShortUrl | None:
        """Deactivate the active short URL with this secret key; return it, or None if absent."""
        ...
