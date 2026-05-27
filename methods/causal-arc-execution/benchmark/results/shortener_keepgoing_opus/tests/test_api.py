"""End-to-end tests for the URL shortener API."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import Settings
from app.db import Database
from app.main import create_app


# ---- /shorten --------------------------------------------------------------

def test_shorten_returns_code_and_short_url(client):
    resp = client.post("/shorten", json={"url": "https://example.com/hello"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "https://example.com/hello"
    assert data["code"] and isinstance(data["code"], str)
    assert data["short_url"].endswith("/" + data["code"])


def test_shorten_is_idempotent_for_same_url(client):
    r1 = client.post("/shorten", json={"url": "https://example.com/a"}).json()
    r2 = client.post("/shorten", json={"url": "https://example.com/a"}).json()
    assert r1["code"] == r2["code"]


def test_shorten_distinct_urls_get_distinct_codes(client):
    a = client.post("/shorten", json={"url": "https://example.com/a"}).json()
    b = client.post("/shorten", json={"url": "https://example.com/b"}).json()
    assert a["code"] != b["code"]


def test_shorten_rejects_invalid_url(client):
    resp = client.post("/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"] == "validation_error"


def test_shorten_rejects_missing_url(client):
    resp = client.post("/shorten", json={})
    assert resp.status_code == 422
    assert resp.json()["error"] == "validation_error"


def test_shorten_rejects_non_http_scheme(client):
    resp = client.post("/shorten", json={"url": "ftp://example.com/x"})
    assert resp.status_code == 422


# ---- GET /{code} (redirect) -----------------------------------------------

def test_redirect_returns_302_to_original(client):
    code = client.post("/shorten", json={"url": "https://example.com/x"}).json()["code"]
    resp = client.get(f"/{code}")
    assert resp.status_code == 302
    assert resp.headers["location"] == "https://example.com/x"


def test_redirect_unknown_code_returns_404(client):
    resp = client.get("/doesnotexist")
    assert resp.status_code == 404
    assert resp.json()["error"] == "not_found"


def test_redirect_invalid_code_returns_404(client):
    # Non-alphanumeric path segments are rejected as not-found.
    resp = client.get("/has-dash")
    assert resp.status_code == 404


# ---- GET /api/stats/{code} -------------------------------------------------

def test_stats_starts_at_zero_clicks(client):
    code = client.post("/shorten", json={"url": "https://example.com/s"}).json()["code"]
    resp = client.get(f"/api/stats/{code}")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"code": code, "url": "https://example.com/s", "clicks": 0}


def test_stats_increments_on_redirect(client):
    code = client.post("/shorten", json={"url": "https://example.com/c"}).json()["code"]
    for _ in range(3):
        assert client.get(f"/{code}").status_code == 302
    body = client.get(f"/api/stats/{code}").json()
    assert body["clicks"] == 3


def test_stats_unknown_code_returns_404(client):
    resp = client.get("/api/stats/missing1")
    assert resp.status_code == 404
    assert resp.json()["error"] == "not_found"


# ---- frontend --------------------------------------------------------------

def test_index_serves_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "URL Shortener" in resp.text


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---- persistence-across-restart -------------------------------------------

def test_persistence_across_restart(tmp_path):
    db_path = str(tmp_path / "persist.db")
    settings = Settings(db_path=db_path, base_url="http://testserver",
                        code_length=7, max_collisions=5)

    # First "process": create + hit a code, then drop the app.
    app1 = create_app(settings=settings, db=Database(db_path))
    with TestClient(app1) as c1:
        if hasattr(c1, "follow_redirects"):
            c1.follow_redirects = False
        code = c1.post("/shorten", json={"url": "https://example.com/p"}).json()["code"]
        assert c1.get(f"/{code}").status_code == 302
        assert c1.get(f"/{code}").status_code == 302

    # Second "process": fresh app + fresh DB handle, same file on disk.
    app2 = create_app(settings=settings, db=Database(db_path))
    with TestClient(app2) as c2:
        if hasattr(c2, "follow_redirects"):
            c2.follow_redirects = False
        stats = c2.get(f"/api/stats/{code}").json()
        assert stats["url"] == "https://example.com/p"
        assert stats["clicks"] == 2
        # And the redirect still works.
        resp = c2.get(f"/{code}")
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://example.com/p"
        # Click count survived and incremented again.
        assert c2.get(f"/api/stats/{code}").json()["clicks"] == 3


# ---- error-response shape consistency -------------------------------------

def test_error_responses_have_consistent_shape(client):
    cases = [
        client.post("/shorten", json={"url": "nope"}),    # 422
        client.get("/api/stats/missing9"),                 # 404
        client.get("/missing99"),                          # 404
    ]
    for resp in cases:
        body = resp.json()
        assert set(body.keys()) == {"error", "detail"}
        assert isinstance(body["error"], str) and body["error"]
