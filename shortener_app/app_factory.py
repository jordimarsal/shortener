# shortener_app/app_factory.py

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .adapters.api.errors import install_error_handlers
from .adapters.api.routes import router
from .adapters.orm import Base
from .adapters.sqlalchemy_repository import SqlAlchemyUrlRepository
from .config import Settings

logger = logging.getLogger(__name__)


def to_async_url(url: str) -> str:
    # sqlite:// becomes sqlite+aiosqlite:// so the engine runs on the async dialect
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


def build_engine(settings: Settings) -> AsyncEngine:
    # aiosqlite serves each query from its own thread, so the event loop never blocks.
    return create_async_engine(to_async_url(settings.db_url), echo=False)


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # takes everything from app.state, so it needs no closures
    async with app.state.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database ready (env=%s)", app.state.settings.env_name)
    yield


def create_app(settings: Settings, engine: AsyncEngine | None = None) -> FastAPI:
    """Composition root: wires the repository adapter into the API and owns the engine."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    application = FastAPI(lifespan=lifespan)
    application.state.settings = settings
    wired_engine = engine if engine is not None else build_engine(settings)
    application.state.engine = wired_engine
    application.state.url_repository = SqlAlchemyUrlRepository(build_session_factory(wired_engine))
    install_error_handlers(application)
    application.include_router(router)
    logger.info(
        "Created application (env=%s, base_url=%s)", settings.env_name, settings.base_url
    )
    return application
