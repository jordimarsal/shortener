# shortener_app/config.py

import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    env_name: str = "Local"
    base_url: str = "http://localhost:8000"
    db_url: str = "sqlite:///./shortener.db"


def get_settings() -> Settings:
    settings = Settings()
    logger.info("Loading settings for: %s", settings.env_name)
    return settings
