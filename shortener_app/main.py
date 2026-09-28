# shortener_app/main.py

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import NoReturn

import validators
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import URL

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import models, schemas
from .service import crud

logger = logging.getLogger(__name__)


# region Bootstrap


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database ready (env=%s)", get_settings().env_name)
    yield


app = FastAPI(lifespan=lifespan)


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


# endregion


# region Routes


@app.get("/")
async def read_root() -> str:
    return "Welcome to the URL shortener API :)"


@app.post("/url", response_model=schemas.URLInfo)
async def create_url(url: schemas.URLBase, db: AsyncSession = Depends(get_db)) -> schemas.URLInfo:
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")
    db_url = await crud.create_db_url(db=db, url=url)
    logger.info("Created short URL key=%s target=%s", db_url.key, db_url.target_url)
    return to_url_info(db_url)


@app.get("/{url_key}")
async def forward_to_target_url(
    url_key: str, request: Request, db: AsyncSession = Depends(get_db)
) -> RedirectResponse:
    if db_url := await crud.get_db_url_by_key(db=db, url_key=url_key):
        await crud.record_click(db=db, url_key=url_key)
        return RedirectResponse(db_url.target_url)
    raise_not_found(request)


@app.get(
    "/admin/{secret_key}",
    name="administration info",
    response_model=schemas.URLInfo,
)
async def get_url_info(
    secret_key: str, request: Request, db: AsyncSession = Depends(get_db)
) -> schemas.URLInfo:
    if db_url := await crud.get_db_url_by_secret_key(db, secret_key=secret_key):
        return to_url_info(db_url)
    raise_not_found(request)


@app.delete("/admin/{secret_key}")
async def delete_url(
    secret_key: str, request: Request, db: AsyncSession = Depends(get_db)
) -> schemas.DeleteUrlResponse:
    db_url = await crud.deactivate_db_url_by_secret_key(db, secret_key=secret_key)
    if db_url is None:
        raise_not_found(request)
    logger.info("Deactivated short URL key=%s", db_url.key)
    return schemas.DeleteUrlResponse(
        detail=f"Successfully deleted shortened URL for '{db_url.target_url}'"
    )


# endregion


# region Presentation


def to_url_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for("administration info", secret_key=db_url.secret_key)
    return schemas.URLInfo(
        target_url=db_url.target_url,
        is_active=db_url.is_active,
        clicks=db_url.clicks,
        url=str(base_url.replace(path=db_url.key)),
        admin_url=str(base_url.replace(path=admin_endpoint)),
    )


# endregion


# region Errors


def raise_bad_request(message: str) -> NoReturn:
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request: Request) -> NoReturn:
    logger.warning("Short URL not found: %s", request.url)
    raise HTTPException(status_code=404, detail=f"URL '{request.url}' doesn't exist")


# endregion
