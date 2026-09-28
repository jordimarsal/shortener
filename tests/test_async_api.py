import inspect

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from shortener_app.database import SessionLocal
from shortener_app.main import app


def _endpoint(path: str, method: str):
    for route in app.routes:
        if route.path == path and method in getattr(route, "methods", set()):
            return route.endpoint
    raise AssertionError(f"Route {method} {path} not found")


def test_create_url_endpoint_is_async():
    assert inspect.iscoroutinefunction(_endpoint("/url", "POST"))


def test_forward_endpoint_is_async():
    assert inspect.iscoroutinefunction(_endpoint("/{url_key}", "GET"))


def test_admin_info_endpoint_is_async():
    assert inspect.iscoroutinefunction(_endpoint("/admin/{secret_key}", "GET"))


def test_delete_endpoint_is_async():
    assert inspect.iscoroutinefunction(_endpoint("/admin/{secret_key}", "DELETE"))


def test_db_session_factory_builds_async_sessions():
    assert issubclass(SessionLocal.class_, AsyncSession)


def test_get_db_is_async_generator():
    from shortener_app.main import get_db

    assert inspect.isasyncgenfunction(get_db)


def test_create_forward_and_delete_flow():
    with TestClient(app) as client:
        resp = client.post("/url", json={"target_url": "https://www.example.com/"})
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["is_active"] is True
        assert data["clicks"] == 0
        key = data["url"].rsplit("/", 1)[-1]
        admin_key = data["admin_url"].rsplit("/", 1)[-1]

        fwd = client.get(f"/{key}", allow_redirects=False)
        assert fwd.status_code in (301, 302, 303, 307)

        info = client.get(f"/admin/{admin_key}")
        assert info.status_code == 200
        assert info.json()["clicks"] == 1

        deleted = client.delete(f"/admin/{admin_key}")
        assert deleted.status_code == 200

        gone = client.get(f"/{key}", allow_redirects=False)
        assert gone.status_code == 404
