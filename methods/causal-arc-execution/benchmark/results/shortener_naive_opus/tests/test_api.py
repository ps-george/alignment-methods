"""Endpoint tests for the URL shortener."""
from fastapi.testclient import TestClient

from app.db import Database
from app.main import create_app


def test_shorten_returns_code_and_short_url(client):
    r = client.post("/shorten", json={"url": "https://example.com/foo"})
    assert r.status_code == 200
    data = r.json()
    assert "code" in data and len(data["code"]) >= 6
    assert data["original_url"] == "https://example.com/foo"
    assert data["short_url"].endswith("/" + data["code"])


def test_shorten_rejects_invalid_url(client):
    r = client.post("/shorten", json={"url": "not a url"})
    assert r.status_code == 422
    body = r.json()
    assert "error" in body
    assert body["error"]["code"] == "validation_error"


def test_shorten_rejects_missing_field(client):
    r = client.post("/shorten", json={})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_redirect_returns_302_and_increments_clicks(client):
    r = client.post("/shorten", json={"url": "https://example.com/a"})
    code = r.json()["code"]

    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 302
    assert r2.headers["location"] == "https://example.com/a"

    stats = client.get(f"/api/stats/{code}").json()
    assert stats["clicks"] == 1

    client.get(f"/{code}", follow_redirects=False)
    client.get(f"/{code}", follow_redirects=False)
    stats = client.get(f"/api/stats/{code}").json()
    assert stats["clicks"] == 3


def test_redirect_404_for_unknown_code(client):
    r = client.get("/doesnotexist", follow_redirects=False)
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "not_found"


def test_stats_404_for_unknown_code(client):
    r = client.get("/api/stats/nope12345")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_stats_returns_original_url_and_zero_clicks_initially(client):
    r = client.post("/shorten", json={"url": "https://example.com/x"})
    code = r.json()["code"]
    stats = client.get(f"/api/stats/{code}").json()
    assert stats["original_url"] == "https://example.com/x"
    assert stats["clicks"] == 0
    assert stats["code"] == code


def test_index_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "URL Shortener" in r.text
    assert "text/html" in r.headers["content-type"]


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_persistence_across_restart(tmp_path):
    db_path = str(tmp_path / "persist.db")

    # First "process": create, shorten, click.
    db1 = Database(db_path)
    app1 = create_app(db=db1)
    with TestClient(app1) as c1:
        code = c1.post("/shorten", json={"url": "https://persist.test/x"}).json()["code"]
        c1.get(f"/{code}", follow_redirects=False)
        c1.get(f"/{code}", follow_redirects=False)
    db1.close()

    # Second "process": new Database against same file.
    db2 = Database(db_path)
    app2 = create_app(db=db2)
    with TestClient(app2) as c2:
        stats = c2.get(f"/api/stats/{code}").json()
        assert stats["original_url"] == "https://persist.test/x"
        assert stats["clicks"] == 2

        # And the redirect still works after restart.
        r = c2.get(f"/{code}", follow_redirects=False)
        assert r.status_code == 302
        assert r.headers["location"] == "https://persist.test/x"
    db2.close()


def test_reserved_paths_do_not_match_redirect(client):
    # /healthz should not be treated as a code.
    r = client.get("/healthz")
    assert r.status_code == 200
    # /shorten via GET should not redirect (it's POST-only).
    r = client.get("/shorten", follow_redirects=False)
    assert r.status_code in (404, 405)
