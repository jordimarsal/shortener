# shortener_app/adapters/api/routes.py

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from ...application import url_service
from ...config import Settings
from ...domain.url import SecretKey, UrlKey
from ...ports.url_repository import UrlRepository
from .deps import get_app_settings, get_url_repository
from .schemas import DeleteUrlResponse, ShortUrlResponse, ShortenUrlRequest, to_response

router = APIRouter()


# region Routes


@router.get("/")
async def read_root() -> str:
    return "Welcome to the URL shortener API :)"


@router.post("/url", response_model=ShortUrlResponse)
async def create_url(
    request: ShortenUrlRequest,
    repo: UrlRepository = Depends(get_url_repository),
    settings: Settings = Depends(get_app_settings),
) -> ShortUrlResponse:
    url = await url_service.shorten_url(repo, request.target_url)
    return to_response(url, base_url=settings.base_url)


@router.get("/{url_key}")
async def forward_to_target_url(
    url_key: str, repo: UrlRepository = Depends(get_url_repository)
) -> RedirectResponse:
    url = await url_service.resolve_url(repo, UrlKey(url_key))
    return RedirectResponse(url.target_url)


@router.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=ShortUrlResponse,
)
async def get_url_info(
    secret_key: str,
    repo: UrlRepository = Depends(get_url_repository),
    settings: Settings = Depends(get_app_settings),
) -> ShortUrlResponse:
    url = await url_service.get_url_info(repo, SecretKey(secret_key))
    return to_response(url, base_url=settings.base_url)


@router.delete("/admin/{secret_key}")
async def delete_url(
    secret_key: str, repo: UrlRepository = Depends(get_url_repository)
) -> DeleteUrlResponse:
    url = await url_service.deactivate_url(repo, SecretKey(secret_key))
    return DeleteUrlResponse(detail=f"Successfully deleted shortened URL for '{url.target_url}'")


# endregion
