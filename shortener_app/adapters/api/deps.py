# shortener_app/adapters/api/deps.py

from typing import cast

from fastapi import Request

from ...config import Settings
from ...ports.url_repository import UrlRepository


def get_url_repository(request: Request) -> UrlRepository:
    # app.state is untyped by starlette; the factory guarantees this attribute.
    return cast(UrlRepository, request.app.state.url_repository)


def get_app_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)
