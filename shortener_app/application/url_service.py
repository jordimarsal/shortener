# shortener_app/application/url_service.py

import logging

from ..domain.errors import KeyGenerationExhaustedError, UrlNotFound
from ..domain.url import (
    MAX_KEY_GENERATION_ATTEMPTS,
    SecretKey,
    ShortUrl,
    UrlKey,
    build_short_url,
    generate_url_key,
    validate_target_url,
)
from ..ports.url_repository import UrlRepository

logger = logging.getLogger(__name__)


# region Use cases


async def shorten_url(repo: UrlRepository, target_url: str) -> ShortUrl:
    validate_target_url(target_url)
    key = await _reserve_unique_key(repo)
    url = await repo.add(build_short_url(target_url, key))
    logger.info("Created short URL key=%s target=%s", url.key, url.target_url)
    return url


async def resolve_url(repo: UrlRepository, key: UrlKey) -> ShortUrl:
    url = await repo.find_by_key(key)
    if url is None:
        raise UrlNotFound("No active short URL matches the given key")
    await repo.record_click(key)
    return url


async def get_url_info(repo: UrlRepository, secret_key: SecretKey) -> ShortUrl:
    url = await repo.find_by_secret_key(secret_key)
    if url is None:
        raise UrlNotFound("No active short URL matches the given secret key")
    return url


async def deactivate_url(repo: UrlRepository, secret_key: SecretKey) -> ShortUrl:
    url = await repo.deactivate(secret_key)
    if url is None:
        raise UrlNotFound("No active short URL matches the given secret key")
    logger.info("Deactivated short URL key=%s", url.key)
    return url


# endregion


# region Helpers


async def _reserve_unique_key(repo: UrlRepository) -> UrlKey:
    for _ in range(MAX_KEY_GENERATION_ATTEMPTS):
        candidate = generate_url_key()
        if await repo.find_by_key(candidate) is None:
            return candidate
    raise KeyGenerationExhaustedError(MAX_KEY_GENERATION_ATTEMPTS)


# endregion
