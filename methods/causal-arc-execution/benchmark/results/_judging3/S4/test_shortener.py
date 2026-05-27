"""Comprehensive pytest test suite for the URL shortener service."""

import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_path(tmp_path):
    return tmp_path / "test_urls.db"


@pytest.fixture()
def client(db_path, monkeypatch):
    """Create a test client backed by an isolated temp database."""
    import main as app_module
    from db import Database

    test_db = Database(db_path)
    test_db.initialize()
    monkeypatch.setattr(app_module, "db", test_db)

    from main import app
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def seeded_client(client):
    """A client that already has one URL shortened."""
    resp = client.post("/shorten", json={"url": "https://example.com/seeded"})
    assert resp.status_code == 201
    data = resp.json()
    return client, data["code"]


# ---------------------------------------------------------------------------
# POST /shorten
# ---------------------------------------------------------------------------

class TestShorten:
    def test_returns_201_with_expected_fields(self, client):
        resp = client.post("/shorten", json={"url": "https://example.com/hello"})
        assert resp.status_code == 201
        data = resp.json()
        assert "code" in data
        assert "short_url" in data
        assert "original_url" in data
        assert data["original_url"] == "https://example.com/hello"
        assert data["code"] in data["short_url"]

    def test_short_code_is_seven_chars(self, client):
        resp = client.post("/shorten", json={"url": "https://example.com/length"})
        assert len(resp.json()["code"]) == 7

    def test_idempotent_same_url_returns_same_code(self, client):
        url = "https://example.com/idempotent"
        r1 = client.post("/shorten", json={"url": url})
        r2 = client.post("/shorten", json={"url": url})
        assert r1.json()["code"] == r2.json()["code"]

    def test_different_urls_get_different_codes(self, client):
        r1 = client.post("/shorten", json={"url": "https://example.com/a"})
        r2 = client.post("/shorten", json={"url": "https://example.com/b"})
        assert r1.json()["code"] != r2.json()["code"]

    # Validation errors
    def test_rejects_missing_body(self, client):
        resp = client.post("/shorten")
        assert resp.status_code == 422

    def test_rejects_empty_url(self, client):
        resp = client.post("/shorten", json={"url": ""})
        assert resp.status_code == 422

    def test_rejects_non_url_string(self, client):
        resp = client.post("/shorten", json={"url": "not-a-url"})
        assert resp.status_code == 422

    def test_rejects_ftp_scheme(self, client):
        resp = client.post("/shorten", json={"url": "ftp://example.com/file"})
        assert resp.status_code == 422

    def test_accepts_http_scheme(self, client):
        resp = client.post("/shorten", json={"url": "http://example.com/page"})
        assert resp.status_code == 201

    def test_accepts_https_scheme(self, client):
        resp = client.post("/shorten", json={"url": "https://example.com/page"})
        assert resp.status_code == 201

    def test_rejects_missing_url_field(self, client):
        resp = client.post("/shorten", json={"link": "https://example.com"})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /{code}
# ---------------------------------------------------------------------------

class TestRedirect:
    def test_redirects_302_to_original(self, seeded_client):
        client, code = seeded_client
        resp = client.get(f"/{code}", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://example.com/seeded"

    def test_redirect_increments_click_count(self, seeded_client):
        client, code = seeded_client
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)
        stats = client.get(f"/api/stats/{code}").json()
        assert stats["click_count"] == 2

    def test_unknown_code_returns_404(self, client):
        resp = client.get("/zzzzzzz", follow_redirects=False)
        assert resp.status_code == 404

    def test_404_has_consistent_error_shape(self, client):
        resp = client.get("/zzzzzzz", follow_redirects=False)
        body = resp.json()
        assert "error" in body


# ---------------------------------------------------------------------------
# GET /api/stats/{code}
# ---------------------------------------------------------------------------

class TestStats:
    def test_returns_stats_for_known_code(self, seeded_client):
        client, code = seeded_client
        resp = client.get(f"/api/stats/{code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == code
        assert data["original_url"] == "https://example.com/seeded"
        assert data["click_count"] == 0

    def test_click_count_starts_at_zero(self, seeded_client):
        client, code = seeded_client
        data = client.get(f"/api/stats/{code}").json()
        assert data["click_count"] == 0

    def test_click_count_reflects_redirects(self, seeded_client):
        client, code = seeded_client
        for _ in range(5):
            client.get(f"/{code}", follow_redirects=False)
        data = client.get(f"/api/stats/{code}").json()
        assert data["click_count"] == 5

    def test_unknown_code_returns_404(self, client):
        resp = client.get("/api/stats/zzzzzzz")
        assert resp.status_code == 404

    def test_404_has_consistent_error_shape(self, client):
        resp = client.get("/api/stats/zzzzzzz")
        body = resp.json()
        assert "error" in body


# ---------------------------------------------------------------------------
# Persistence across restart
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_data_survives_db_reconnect(self, db_path, monkeypatch):
        """
        Simulate a service restart: write data via one Database instance,
        then read it back via a fresh instance pointing at the same file.
        """
        import main as app_module
        from db import Database
        from main import app

        # First "run" — insert a URL
        db1 = Database(db_path)
        db1.initialize()
        monkeypatch.setattr(app_module, "db", db1)

        with TestClient(app) as c1:
            resp = c1.post("/shorten", json={"url": "https://persist.example.com/"})
            assert resp.status_code == 201
            code = resp.json()["code"]
            # Do a click so we have non-zero count to verify
            c1.get(f"/{code}", follow_redirects=False)

        # Second "run" — fresh Database instance, same file path
        db2 = Database(db_path)
        db2.initialize()
        monkeypatch.setattr(app_module, "db", db2)

        with TestClient(app) as c2:
            stats = c2.get(f"/api/stats/{code}")
            assert stats.status_code == 200
            data = stats.json()
            assert data["original_url"] == "https://persist.example.com/"
            assert data["click_count"] == 1


# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

class TestFrontend:
    def test_root_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert "<form" in resp.text or "shortenUrl" in resp.text
