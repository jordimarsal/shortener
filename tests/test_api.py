# tests/test_api.py

from fastapi.testclient import TestClient


def test_root_welcomes(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "URL shortener" in response.text


def test_create_forward_and_delete_flow(client: TestClient) -> None:
    created = client.post("/url", json={"target_url": "https://www.example.com/"})
    assert created.status_code == 200, created.text
    data = created.json()
    assert data["is_active"] is True
    assert data["clicks"] == 0
    key = data["url"].rsplit("/", 1)[-1]
    admin_key = data["admin_url"].rsplit("/", 1)[-1]

    forwarded = client.get(f"/{key}", follow_redirects=False)
    assert forwarded.status_code == 307
    assert forwarded.headers["location"] == "https://www.example.com/"

    info = client.get(f"/admin/{admin_key}")
    assert info.status_code == 200
    assert info.json()["clicks"] == 1

    deleted = client.delete(f"/admin/{admin_key}")
    assert deleted.status_code == 200

    gone = client.get(f"/{key}", follow_redirects=False)
    assert gone.status_code == 404


def test_create_url_rejects_invalid_target_with_400(client: TestClient) -> None:
    rejected = client.post("/url", json={"target_url": "not a url at all"})
    assert rejected.status_code == 400
    assert rejected.json()["detail"] == "Your provided URL is not valid"


def test_forward_unknown_key_returns_404(client: TestClient) -> None:
    missing = client.get("/ZZZZZ", follow_redirects=False)
    assert missing.status_code == 404
    assert "doesn't exist" in missing.json()["detail"]


def test_admin_info_unknown_secret_returns_404(client: TestClient) -> None:
    assert client.get("/admin/NOPE_MISSING").status_code == 404


def test_delete_unknown_secret_returns_404(client: TestClient) -> None:
    assert client.delete("/admin/NOPE_MISSING").status_code == 404


def test_second_delete_of_same_url_returns_404(client: TestClient) -> None:
    created = client.post("/url", json={"target_url": "https://www.example.com/"})
    admin_key = created.json()["admin_url"].rsplit("/", 1)[-1]

    first = client.delete(f"/admin/{admin_key}")
    assert first.status_code == 200

    second = client.delete(f"/admin/{admin_key}")
    assert second.status_code == 404
