# Shortener

Async URL shortener API with a hexagonal-lite architecture: FastAPI endpoints
(`async def`) over SQLAlchemy `AsyncSession` on `aiosqlite`, so database I/O
never blocks the event loop.

## Architecture

```
                 inbound                       core (pure)                outbound
┌──────────────────────────┐   ┌────────────────────────────────────┐   ┌──────────────────────────┐
│ adapters/api             │   │ application/url_service            │   │ adapters/                │
│  routes (thin endpoints) │──▶│  shorten_url / resolve_url /       │──▶│  sqlalchemy_repository   │
│  schemas (request/respo) │   │  get_url_info / deactivate_url     │   │   implements the port    │
│  errors (domain → HTTP)  │   │ domain/                            │   │  orm (UrlRecord table)   │
└──────────────────────────┘   │  ShortUrl (frozen dataclass),      │   └──────────────────────────┘
        dependency             │  UrlKey/SecretKey, keygen, errors  │            depends on
        injection              └──────────────┬─────────────────────┘
                                               │ defines
                                      ┌────────▼─────────┐
                                      │ ports/           │
                                      │  UrlRepository   │
                                      │  Protocol        │
                                      └──────────────────┘
```

Why this shape:

- **Pure core** (`domain/` + `application/`): no framework imports, deterministic
  and unit-testable without I/O. Semantic types (`UrlKey`, `SecretKey`) and an
  immutable entity replace primitive-string soup.
- **Port** (`ports/url_repository.py`): the core defines what persistence means;
  adapters decide how. Swapping SQLite for Postgres touches one adapter only.
- **Adapters**: SQLAlchemy repository on one side, thin FastAPI routes on the
  other. Domain errors map to HTTP status codes (400/404/503) via exception
  handlers, so use cases never import FastAPI.
- **Composition root** (`app_factory.create_app`): owns the engine wiring and
  accepts an injected `AsyncEngine`, which lets tests run against in-memory
  SQLite instead of monkeypatching module-level singletons.

## Install:

```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Run:

```sh
$ source venv/bin/activate (if not activated)
$ uvicorn shortener_app.main:app --reload
```

### Browser:

http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc

## Tests, types, lint:

```sh
$ source venv/bin/activate (if not activated)
$ python -m pytest tests/ -v
$ python -m mypy   # strict mode, configured in pyproject.toml
$ python -m ruff check .   # lint (import order, bugbear, simplify, ...)
```

## Example:
Post:
```sh
curl -X 'POST' \
  'http://127.0.0.1:8000/url' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "target_url": "http://www.jordimp.net/"
}'
```

Response body:
```json
{
  "target_url": "http://www.jordimp.net/",
  "is_active": true,
  "clicks": 0,
  "url": "http://127.0.0.1:8000/ERW8S",
  "admin_url": "http://127.0.0.1:8000/admin/ERW8S_BD6EZEUN"
}
```
