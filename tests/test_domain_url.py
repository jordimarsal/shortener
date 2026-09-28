# tests/test_domain_url.py

import dataclasses

import pytest

from shortener_app.domain.errors import InvalidTargetUrl
from shortener_app.domain.url import (
    MAX_TARGET_URL_LENGTH,
    SECRET_KEY_SEPARATOR,
    UrlKey,
    build_short_url,
    compose_secret_key,
    validate_target_url,
)


def test_validate_target_url_accepts_https_urls() -> None:
    validate_target_url("https://www.example.com/")  # does not raise


def test_validate_target_url_rejects_plain_text() -> None:
    with pytest.raises(InvalidTargetUrl):
        validate_target_url("not a url at all")


def test_validate_target_url_rejects_non_http_schemes() -> None:
    with pytest.raises(InvalidTargetUrl):
        validate_target_url("ftp://ftp.example.com/file")


def test_validate_target_url_accepts_uppercase_https_scheme() -> None:
    validate_target_url("HTTPS://WWW.EXAMPLE.COM/path")  # does not raise


def test_validate_target_url_accepts_exactly_max_length() -> None:
    prefix = "https://www.example.com/"
    longest = f"{prefix}{'a' * (MAX_TARGET_URL_LENGTH - len(prefix))}"
    assert len(longest) == MAX_TARGET_URL_LENGTH
    validate_target_url(longest)  # does not raise


def test_validate_target_url_rejects_oversized_urls() -> None:
    oversized = f"https://www.example.com/{'a' * MAX_TARGET_URL_LENGTH}"
    with pytest.raises(InvalidTargetUrl):
        validate_target_url(oversized)


def test_validate_target_url_error_carries_the_offending_value() -> None:
    with pytest.raises(InvalidTargetUrl) as error:
        validate_target_url("nope")
    assert error.value.target_url == "nope"


def test_compose_secret_key_joins_key_and_suffix() -> None:
    assert compose_secret_key(UrlKey("ABC12"), "XYZ89") == f"ABC12{SECRET_KEY_SEPARATOR}XYZ89"


def test_build_short_url_starts_active_with_zero_clicks() -> None:
    url = build_short_url("https://www.example.com/", UrlKey("ABC12"))
    assert url.is_active is True
    assert url.clicks == 0
    assert url.target_url == "https://www.example.com/"
    assert url.key == "ABC12"
    assert url.secret_key.startswith("ABC12_")


def test_short_url_is_frozen() -> None:
    url = build_short_url("https://www.example.com/", UrlKey("ABC12"))
    with pytest.raises(dataclasses.FrozenInstanceError):
        # deliberate violation: proves the dataclass is frozen at runtime
        url.clicks = 5  # type: ignore[misc]
