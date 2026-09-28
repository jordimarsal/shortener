# shortener_app/database.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import get_settings


def to_async_url(url: str) -> str:
    # sqlite:// becomes sqlite+aiosqlite:// so the engine runs on the async dialect
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    return url


# aiosqlite serves each query from its own thread, so the event loop never blocks.
engine = create_async_engine(to_async_url(get_settings().db_url), echo=False)
# factory of async database sessions
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)
# connects the models to the database
Base = declarative_base()
