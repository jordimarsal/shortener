# tests/conftest.py

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool

from shortener_app.app_factory import create_app
from shortener_app.config import Settings

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


def build_test_engine() -> AsyncEngine:
    # StaticPool keeps one shared connection so the in-memory database is the
    # same for schema creation and for every session; state never leaks to disk.
    return create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture
def settings() -> Settings:
    return Settings(env_name="Test", base_url="http://testserver", db_url=TEST_DB_URL)


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    return create_app(settings, engine=build_test_engine())


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
