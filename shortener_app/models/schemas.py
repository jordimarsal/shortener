# shortener_app/models/schemas.py

from pydantic import BaseModel, ConfigDict


class URLBase(BaseModel):
    target_url: str


class URL(URLBase):
    model_config = ConfigDict(from_attributes=True)

    is_active: bool
    clicks: int


class URLInfo(URL):
    url: str
    admin_url: str


class DeleteUrlResponse(BaseModel):
    detail: str
