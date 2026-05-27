"""Comprehensive tests for the URL Shortener API."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# Use a temp DB for tests
os.environ["DB_PATH"] = ""  # Will be overridden per test


@pytest.fixture()
def tmp_db(tmp_path):
    """Provide a temp SQLite path and set DB_PATH env var."""
    db_file = str(tmp_path / "test.db")
    os.environ["DB_PATH"] = db_file
    yield db_file
    if os.path.exists(db_file):
        os.remove(db_file)


@pytest.fixture()
def client(tmp_db):
    """Create a fresh TestClient with an isolated database."""
    # Re-import to pick up new DB_PATH
    import importlib
    import database as db_module
    import main as main_module

    importlib.reload(db_module)
    importlib.reload(main_module)

    from main import app, db
    db.db_path = tmp_db
    db.init()

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# POST /shorten
# ---------------------------------------------------------------------------

class TestShortenEndpoint:
    def test_shorten_valid_url_returns_code_and_short_url(self, client):
        resp = client.post("/shorten", json={"url": "https://example.com/path"})
        assert resp.status_code == 200
        data = resp.json()
        assert "code" in data
        assert "short_url" in data
        assert "original_url" in data
        assert data["original_url"] == "https://example.com/path"
        assert data["code"] in data["short_url"]

    def test_shorten_returns_existing_code_for_duplicate_url(self, client):
        r1 = client.post("/shorten", json={"url": "https://example.com/dup"})
        r2 = client.post("/shorten", json={"url": "https://example.com/dup"})
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["code"] == r2.json()["code"]

    def test_shorten_different_urls_get_different_codes(self, client):
        r1 = client.post("/shorten", json={"url": "https://example.com/a"})
        r2 = client.post("/shorten", json={"url": "https://example.com/b"})
        assert r1.json()["code"] != r2.json()["code"]

    def test_shorten_invalid_url_returns_422(self, client):
        resp = client.post("/shorten", json={"url": "not-a-url"})
        assert resp.status_code == 422

    def test_shorten_empty_body_returns_422(self, client):
        resp = client.post("/shorten", json={})
        assert resp.status_code == 422

    def test_shorten_missing_scheme_returns_422(self, client):
        resp = client.post("/shorten", json={"url": "example.com/path"})
        assert resp.status_code == 422

    def test_shorten_ftp_url_returns_422(self, client):
        resp = client.post("/shorten", json={"url": "ftp://example.com/file"})
        assert resp.status_code == 422

    def test_shorten_http_url_accepted(self, client):
        resp = client.post("/shorten", json={"url": "http://example.com/plain"})
        assert resp.status_code == 200

    def test_shorten_short_url_contains_base(self, client):
        resp = client.post("/shorten", json={"url": "https://example.com"})
        assert resp.status_code == 200
        assert resp.json()["short_url"].startswith("http")


# ---------------------------------------------------------------------------
# GET /{code}
# ---------------------------------------------------------------------------

class TestRedirectEndpoint:
    def test_redirect_existing_code(self, client):
        shorten = client.post("/shorten", json={"url": "https://target.example.com"})
        code = shorten.json()["code"]
        resp = client.get(f"/{code}", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "https://target.example.com"

    def test_redirect_unknown_code_returns_404(self, client):
        resp = client.get("/doesnotexist", follow_redirects=False)
        assert resp.status_code == 404

    def test_redirect_increments_click_count(self, client):
        shorten = client.post("/shorten", json={"url": "https://click.example.com"})
        code = shorten.json()["code"]

        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)

        stats = client.get(f"/api/stats/{code}").json()
        assert stats["click_count"] == 3

    def test_redirect_404_has_consistent_error_shape(self, client):
        resp = client.get("/badcode", follow_redirects=False)
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data


# ---------------------------------------------------------------------------
# GET /api/stats/{code}
# ---------------------------------------------------------------------------

class TestStatsEndpoint:
    def test_stats_for_new_code_has_zero_clicks(self, client):
        shorten = client.post("/shorten", json={"url": "https://stats.example.com"})
        code = shorten.json()["code"]
        resp = client.get(f"/api/stats/{code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["click_count"] == 0
        assert data["original_url"] == "https://stats.example.com"
        assert data["code"] == code

    def test_stats_unknown_code_returns_404(self, client):
        resp = client.get("/api/stats/unknown123")
        assert resp.status_code == 404

    def test_stats_404_has_consistent_error_shape(self, client):
        resp = client.get("/api/stats/ghost")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_stats_click_count_updates_after_redirects(self, client):
        shorten = client.post("/shorten", json={"url": "https://count.example.com"})
        code = shorten.json()["code"]

        for _ in range(5):
            client.get(f"/{code}", follow_redirects=False)

        resp = client.get(f"/api/stats/{code}")
        assert resp.json()["click_count"] == 5


# ---------------------------------------------------------------------------
# Persistence across restart
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_data_persists_across_app_restart(self, tmp_db):
        """Simulate a restart by creating two separate TestClients on the same DB."""
        import importlib
        import database as db_module
        import main as main_module

        # First "session": create a short URL
        importlib.reload(db_module)
        importlib.reload(main_module)
        from main import app as app1, db as db1
        db1.db_path = tmp_db
        db1.init()

        code = None
        with TestClient(app1) as c1:
            r = c1.post("/shorten", json={"url": "https://persist.example.com"})
            code = r.json()["code"]
            # also record a click
            c1.get(f"/{code}", follow_redirects=False)

        # Second "session": fresh module reload simulates restart
        importlib.reload(db_module)
        importlib.reload(main_module)
        from main import app as app2, db as db2
        db2.db_path = tmp_db
        db2.init()

        with TestClient(app2) as c2:
            r2 = c2.get(f"/{code}", follow_redirects=False)
            assert r2.status_code == 302

            stats = c2.get(f"/api/stats/{code}").json()
            assert stats["original_url"] == "https://persist.example.com"
            # click recorded in first session + one in second session
            assert stats["click_count"] == 2


# ---------------------------------------------------------------------------
# HTML frontend
# ---------------------------------------------------------------------------

class TestFrontend:
    def test_root_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]
        assert b"<html" in resp.content.lower()

    def test_root_contains_form_elements(self, client):
        resp = client.get("/")
        assert b"shorten" in resp.content.lower() or b"url" in resp.content.lower()
