# shortener_app/adapters/api/errors.py

import logging
from typing import cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ...domain.errors import InvalidTargetUrl, KeyGenerationExhaustedError, UrlNotFound

logger = logging.getLogger(__name__)


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(InvalidTargetUrl, _handle_invalid_target_url)
    app.add_exception_handler(UrlNotFound, _handle_url_not_found)
    app.add_exception_handler(KeyGenerationExhaustedError, _handle_key_generation_exhausted)


async def _handle_invalid_target_url(_: Request, error: Exception) -> JSONResponse:
    rejected = cast(InvalidTargetUrl, error)
    logger.warning("Rejected invalid target URL (%s chars)", len(rejected.target_url))
    return JSONResponse(status_code=400, content={"detail": "Your provided URL is not valid"})


async def _handle_url_not_found(request: Request, __: Exception) -> JSONResponse:
    logger.warning("Short URL not found: %s", request.url)
    return JSONResponse(status_code=404, content={"detail": f"URL '{request.url}' doesn't exist"})


async def _handle_key_generation_exhausted(_: Request, error: Exception) -> JSONResponse:
    exhausted = cast(KeyGenerationExhaustedError, error)
    logger.error("Key generation exhausted after %s attempts", exhausted.attempts)
    return JSONResponse(
        status_code=503,
        content={"detail": "Could not generate a unique short URL key, please retry"},
    )
