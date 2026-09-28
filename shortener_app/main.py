# shortener_app/main.py

from .app_factory import create_app
from .config import get_settings

# Composition root entrypoint for uvicorn: shortener_app.main:app
app = create_app(get_settings())
