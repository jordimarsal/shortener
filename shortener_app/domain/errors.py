# shortener_app/domain/errors.py


class DomainError(Exception):
    """Base class for domain rule violations."""


class InvalidTargetUrl(DomainError):
    """Raised when a target URL does not pass validation."""

    def __init__(self, target_url: str) -> None:
        self.target_url = target_url
        super().__init__("Your provided URL is not valid")


class UrlNotFound(DomainError):
    """Raised when no active short URL matches a key or a secret key."""


class KeyGenerationExhaustedError(DomainError):
    """Raised when unique key generation fails after the maximum number of attempts."""

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts
        super().__init__(f"Could not generate a unique key after {attempts} attempts")
