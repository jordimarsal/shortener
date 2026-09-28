# Shortener

Async URL shortener API: FastAPI endpoints (`async def`) with SQLAlchemy `AsyncSession`
over `aiosqlite`, so database I/O never blocks the event loop.

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

## Tests:

```sh
$ source venv/bin/activate (if not activated)
$ python -m pytest tests/ -v
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