# shortener_app/adapters/api/schemas.py

from pydantic import BaseModel

from ...domain.url import ShortUrl

ADMIN_PATH_PREFIX = "/admin/"


class ShortenUrlRequest(BaseModel):
    target_url: str


class ShortUrlResponse(BaseModel):
    target_url: str
    is_active: bool
    clicks: int
    url: str
    admin_url: str


class DeleteUrlResponse(BaseModel):
    detail: str


def to_response(url: ShortUrl, base_url: str) -> ShortUrlResponse:
    root = base_url.rstrip("/")
    return ShortUrlResponse(
        target_url=url.target_url,
        is_active=url.is_active,
        clicks=url.clicks,
        url=f"{root}/{url.key}",
        admin_url=f"{root}{ADMIN_PATH_PREFIX}{url.secret_key}",
    )
