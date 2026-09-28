# tests/test_api.py

from fastapi.testclient import TestClient


def test_root_welcomes(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "URL shortener" in response.text


def test_create_forward_and_delete_flow(client: TestClient):
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
