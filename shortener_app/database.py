# shortener_app/database.py

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import Settings, get_settings


def to_async_url(url: str) -> str:
    # sqlite:// becomes sqlite+aiosqlite:// so the engine runs on the async dialect
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


def build_engine(settings: Settings) -> AsyncEngine:
    # aiosqlite serves each query from its own thread, so the event loop never blocks.
    return create_async_engine(to_async_url(settings.db_url), echo=False)


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # factory of async database sessions
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


class Base(DeclarativeBase):
    """Connects the models to the database."""


# transitional module-level wiring: replaced by the app factory in phase 2
engine = build_engine(get_settings())
SessionLocal = build_session_factory(engine)
