# shortener_app/service/crud.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import models, schemas
from ..utils import keygen


async def create_db_url(db: AsyncSession, url: schemas.URLBase) -> models.URL:
    key = await create_unique_random_key(db)
    secret_key = f"{key}_{keygen.create_random_key(length=8)}"
    db_url = models.URL(target_url=url.target_url, key=key, secret_key=secret_key)
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    return db_url


async def get_db_url_by_key(db: AsyncSession, url_key: str) -> models.URL | None:
    result = await db.execute(
        select(models.URL).where(models.URL.key == url_key, models.URL.is_active)
    )
    return result.scalars().first()


async def create_unique_random_key(db: AsyncSession) -> str:
    key = keygen.create_random_key()
    while await get_db_url_by_key(db, key):
        key = keygen.create_random_key()
    return key


async def get_db_url_by_secret_key(db: AsyncSession, secret_key: str) -> models.URL | None:
    result = await db.execute(
        select(models.URL).where(
            models.URL.secret_key == secret_key, models.URL.is_active
        )
    )
    return result.scalars().first()


async def update_db_clicks(db: AsyncSession, db_url: models.URL) -> models.URL:
    db_url.clicks += 1
    await db.commit()
    await db.refresh(db_url)
    return db_url


async def deactivate_db_url_by_secret_key(db: AsyncSession, secret_key: str) -> models.URL | None:
    db_url = await get_db_url_by_secret_key(db, secret_key)
    if db_url:
        db_url.is_active = False
        await db.commit()
        await db.refresh(db_url)
    return db_url
