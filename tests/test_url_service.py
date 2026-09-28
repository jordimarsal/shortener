# tests/test_url_service.py

import pytest
from fake_url_repository import FakeUrlRepository

from shortener_app.application import url_service
from shortener_app.domain.errors import (
    InvalidTargetUrl,
    KeyGenerationExhaustedError,
    UrlNotFound,
)
from shortener_app.domain.url import (
    MAX_KEY_GENERATION_ATTEMPTS,
    SECRET_KEY_SEPARATOR,
    SECRET_KEY_SUFFIX_LENGTH,
    SecretKey,
    UrlKey,
    build_short_url,
)


@pytest.fixture
def repo() -> FakeUrlRepository:
    return FakeUrlRepository()


# region shorten_url


async def test_shorten_url_saves_active_url_with_composed_secret(repo: FakeUrlRepository) -> None:
    url = await url_service.shorten_url(repo, "https://www.example.com/")

    assert repo.saved == [url]
    assert url.is_active is True
    assert url.clicks == 0
    secret_prefix = f"{url.key}{SECRET_KEY_SEPARATOR}"
    assert url.secret_key.startswith(secret_prefix)
    assert len(url.secret_key) == len(secret_prefix) + SECRET_KEY_SUFFIX_LENGTH


async def test_shorten_url_rejects_invalid_target_without_saving(repo: FakeUrlRepository) -> None:
    with pytest.raises(InvalidTargetUrl):
        await url_service.shorten_url(repo, "not a url at all")
    assert repo.saved == []


async def test_shorten_url_regenerates_key_on_collision(
    monkeypatch: pytest.MonkeyPatch, repo: FakeUrlRepository
) -> None:
    seeded = build_short_url("https://taken.example/", UrlKey("TAKEN"))
    repo._urls[seeded.key] = seeded
    generated = iter([UrlKey("TAKEN"), UrlKey("FRESH")])
    monkeypatch.setattr(url_service, "generate_url_key", lambda: next(generated))

    url = await url_service.shorten_url(repo, "https://www.example.com/")

    assert url.key == "FRESH"


async def test_shorten_url_raises_after_max_attempts_without_saving(
    monkeypatch: pytest.MonkeyPatch, repo: FakeUrlRepository
) -> None:
    seeded = build_short_url("https://taken.example/", UrlKey("TAKEN"))
    repo._urls[seeded.key] = seeded
    monkeypatch.setattr(url_service, "generate_url_key", lambda: UrlKey("TAKEN"))

    with pytest.raises(KeyGenerationExhaustedError) as error:
        await url_service.shorten_url(repo, "https://www.example.com/")

    assert error.value.attempts == MAX_KEY_GENERATION_ATTEMPTS
    assert repo.saved == []


# endregion


# region resolve_url


async def test_resolve_url_returns_url_and_records_click(repo: FakeUrlRepository) -> None:
    url = await url_service.shorten_url(repo, "https://www.example.com/")

    resolved = await url_service.resolve_url(repo, url.key)

    assert resolved.key == url.key
    assert await repo.find_by_key(url.key) is not None
    stored = repo._urls[url.key]
    assert stored.clicks == 1


async def test_resolve_url_raises_for_unknown_key(repo: FakeUrlRepository) -> None:
    with pytest.raises(UrlNotFound):
        await url_service.resolve_url(repo, UrlKey("NOPE1"))


async def test_resolve_url_raises_for_deactivated_url(repo: FakeUrlRepository) -> None:
    url = await url_service.shorten_url(repo, "https://www.example.com/")
    await url_service.deactivate_url(repo, url.secret_key)

    with pytest.raises(UrlNotFound):
        await url_service.resolve_url(repo, url.key)


# endregion


# region get_url_info


async def test_get_url_info_returns_url_for_secret_key(repo: FakeUrlRepository) -> None:
    url = await url_service.shorten_url(repo, "https://www.example.com/")

    found = await url_service.get_url_info(repo, url.secret_key)

    assert found.key == url.key


async def test_get_url_info_raises_for_unknown_secret_key(repo: FakeUrlRepository) -> None:
    with pytest.raises(UrlNotFound):
        await url_service.get_url_info(repo, SecretKey("NOPE1_MISSING"))


# endregion


# region deactivate_url


async def test_deactivate_url_marks_url_inactive(repo: FakeUrlRepository) -> None:
    url = await url_service.shorten_url(repo, "https://www.example.com/")

    deactivated = await url_service.deactivate_url(repo, url.secret_key)

    assert deactivated is not None and deactivated.is_active is False
    assert await repo.find_by_secret_key(url.secret_key) is None


async def test_deactivate_url_raises_for_unknown_secret_key(repo: FakeUrlRepository) -> None:
    with pytest.raises(UrlNotFound):
        await url_service.deactivate_url(repo, SecretKey("NOPE1_MISSING"))


# endregion
