# shortener_app/adapters/sqlalchemy_repository.py

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.sql.elements import ColumnElement

from ..domain.url import SecretKey, ShortUrl, UrlKey
from ..ports.url_repository import UrlRepository
from .orm import UrlRecord

# region Mapping helpers


def _to_domain(record: UrlRecord) -> ShortUrl:
    return ShortUrl(
        key=UrlKey(record.key),
        secret_key=SecretKey(record.secret_key),
        target_url=record.target_url,
        is_active=record.is_active,
        clicks=record.clicks,
    )


async def _find_active(session: AsyncSession, criterion: ColumnElement[bool]) -> UrlRecord | None:
    result = await session.execute(select(UrlRecord).where(criterion, UrlRecord.is_active.is_(True)))
    return result.scalars().first()


# endregion


# region Repository


class SqlAlchemyUrlRepository(UrlRepository):
    """SQLAlchemy adapter of the UrlRepository port.

    Each operation runs in its own session, keeping use cases free of
    session lifecycle concerns at the cost of one transaction per call.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def add(self, url: ShortUrl) -> ShortUrl:
        async with self._session_factory() as session:
            record = UrlRecord(key=url.key, secret_key=url.secret_key, target_url=url.target_url)
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return _to_domain(record)

    async def find_by_key(self, key: UrlKey) -> ShortUrl | None:
        async with self._session_factory() as session:
            record = await _find_active(session, UrlRecord.key == key)
            return _to_domain(record) if record else None

    async def find_by_secret_key(self, secret_key: SecretKey) -> ShortUrl | None:
        async with self._session_factory() as session:
            record = await _find_active(session, UrlRecord.secret_key == secret_key)
            return _to_domain(record) if record else None

    async def record_click(self, key: UrlKey) -> None:
        # Atomic increment: a read-modify-write on the ORM object loses counts
        # when two requests race for the same key.
        statement = (
            update(UrlRecord)
            .where(UrlRecord.key == key, UrlRecord.is_active.is_(True))
            .values(clicks=UrlRecord.clicks + 1)
        )
        async with self._session_factory() as session:
            await session.execute(statement)
            await session.commit()

    async def deactivate(self, secret_key: SecretKey) -> ShortUrl | None:
        async with self._session_factory() as session:
            record = await _find_active(session, UrlRecord.secret_key == secret_key)
            if record is None:
                return None
            record.is_active = False
            await session.commit()
            await session.refresh(record)
            return _to_domain(record)


# endregion
