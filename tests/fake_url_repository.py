# tests/fake_url_repository.py

from dataclasses import replace

from shortener_app.domain.url import SecretKey, ShortUrl, UrlKey
from shortener_app.ports.url_repository import UrlRepository


class FakeUrlRepository:
    """In-memory implementation of the UrlRepository port for use case tests."""

    def __init__(self) -> None:
        self._urls: dict[UrlKey, ShortUrl] = {}
        self.saved: list[ShortUrl] = []

    async def add(self, url: ShortUrl) -> ShortUrl:
        self.saved.append(url)
        self._urls[url.key] = url
        return url

    async def find_by_key(self, key: UrlKey) -> ShortUrl | None:
        url = self._urls.get(key)
        return url if url is not None and url.is_active else None

    async def find_by_secret_key(self, secret_key: SecretKey) -> ShortUrl | None:
        for url in self._urls.values():
            if url.secret_key == secret_key and url.is_active:
                return url
        return None

    async def record_click(self, key: UrlKey) -> None:
        url = self._urls[key]
        self._urls[key] = replace(url, clicks=url.clicks + 1)

    async def deactivate(self, secret_key: SecretKey) -> ShortUrl | None:
        url = await self.find_by_secret_key(secret_key)
        if url is None:
            return None
        inactive = replace(url, is_active=False)
        self._urls[url.key] = inactive
        return inactive
