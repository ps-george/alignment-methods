"""Comprehensive tests for the URL Shortener API."""

import os
import sqlite3
import tempfile

# Must set DB_PATH before importing app/database so the module-level Database()
# instance picks up the right path.
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["DB_PATH"] = _tmp_db.name

import pytest
from fastapi.testclient import TestClient

from database import Database
from main import app, db


@pytest.fixture(autouse=True)
def fresh_db():
    """Wipe and re-create the urls table before every test."""
    conn = sqlite3.connect(os.environ["DB_PATH"])
    conn.execute("DROP TABLE IF EXISTS urls")
    conn.commit()
    conn.close()
    db.db_path = os.environ["DB_PATH"]
    db.init_db()
    yield


@pytest.fixture
def client(fresh_db):
    with TestClient(app) as c:
        yield c


# --- POST /shorten ---

class TestShortenEndpoint:
    def test_shorten_valid_url(self, client):
        res = client.post("/shorten", json={"url": "https://example.com"})
        assert res.status_code == 201
        data = res.json()
        assert "short_code" in data
        assert "short_url" in data
        assert "original_url" in data
        assert data["original_url"] == "https://example.com"
        assert len(data["short_code"]) == 7
        assert data["short_code"] in data["short_url"]

    def test_shorten_returns_full_short_url(self, client):
        res = client.post("/shorten", json={"url": "https://example.com/path?q=1"})
        assert res.status_code == 201
        data = res.json()
        assert data["short_url"].startswith("http")
        assert data["short_url"].endswith(data["short_code"])

    def test_shorten_invalid_url_missing_scheme(self, client):
        res = client.post("/shorten", json={"url": "example.com"})
        assert res.status_code == 422

    def test_shorten_invalid_url_empty(self, client):
        res = client.post("/shorten", json={"url": ""})
        assert res.status_code == 422

    def test_shorten_missing_url_field(self, client):
        res = client.post("/shorten", json={})
        assert res.status_code == 422

    def test_shorten_non_json_body(self, client):
        res = client.post(
            "/shorten",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        assert res.status_code == 422

    def test_shorten_http_url(self, client):
        res = client.post("/shorten", json={"url": "http://example.com"})
        assert res.status_code == 201

    def test_shorten_url_with_path_and_query(self, client):
        url = "https://www.google.com/search?q=url+shortener&lang=en"
        res = client.post("/shorten", json={"url": url})
        assert res.status_code == 201
        assert res.json()["original_url"] == url


# --- GET /{code} ---

class TestRedirectEndpoint:
    def test_redirect_valid_code(self, client):
        post = client.post("/shorten", json={"url": "https://example.com"})
        code = post.json()["short_code"]

        res = client.get(f"/{code}", follow_redirects=False)
        assert res.status_code == 302
        assert res.headers["location"] == "https://example.com"

    def test_redirect_increments_click_count(self, client):
        post = client.post("/shorten", json={"url": "https://example.com"})
        code = post.json()["short_code"]

        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)

        stats = client.get(f"/api/stats/{code}")
        assert stats.json()["click_count"] == 3

    def test_redirect_unknown_code_404(self, client):
        res = client.get("/nonexistent", follow_redirects=False)
        assert res.status_code == 404

    def test_redirect_404_error_shape(self, client):
        res = client.get("/badcode", follow_redirects=False)
        data = res.json()
        assert "error" in data

    def test_redirect_does_not_follow_internally(self, client):
        post = client.post("/shorten", json={"url": "https://example.com"})
        code = post.json()["short_code"]
        res = client.get(f"/{code}", follow_redirects=False)
        assert res.status_code == 302


# --- GET /api/stats/{code} ---

class TestStatsEndpoint:
    def test_stats_for_valid_code(self, client):
        post = client.post("/shorten", json={"url": "https://example.com"})
        code = post.json()["short_code"]

        res = client.get(f"/api/stats/{code}")
        assert res.status_code == 200
        data = res.json()
        assert data["short_code"] == code
        assert data["original_url"] == "https://example.com"
        assert data["click_count"] == 0

    def test_stats_click_count_starts_at_zero(self, client):
        post = client.post("/shorten", json={"url": "https://example.com"})
        code = post.json()["short_code"]
        stats = client.get(f"/api/stats/{code}")
        assert stats.json()["click_count"] == 0

    def test_stats_unknown_code_404(self, client):
        res = client.get("/api/stats/doesnotexist")
        assert res.status_code == 404

    def test_stats_404_error_shape(self, client):
        res = client.get("/api/stats/badcode")
        data = res.json()
        assert "error" in data

    def test_stats_after_redirects(self, client):
        post = client.post("/shorten", json={"url": "https://example.com"})
        code = post.json()["short_code"]

        for _ in range(5):
            client.get(f"/{code}", follow_redirects=False)

        stats = client.get(f"/api/stats/{code}")
        assert stats.json()["click_count"] == 5


# --- GET / (frontend) ---

class TestFrontend:
    def test_index_returns_html(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        assert "<form" in res.text

    def test_index_contains_shorten_form(self, client):
        res = client.get("/")
        assert "shorten" in res.text.lower()


# --- Persistence across restart ---

class TestPersistence:
    def test_data_persists_after_recreating_db_instance(self, client):
        """Simulate a server restart by creating a new Database instance on same file."""
        post = client.post("/shorten", json={"url": "https://persistent.example.com"})
        assert post.status_code == 201
        code = post.json()["short_code"]

        # Click the URL a couple times
        client.get(f"/{code}", follow_redirects=False)
        client.get(f"/{code}", follow_redirects=False)

        # Create a fresh Database instance pointing to the same file
        new_db = Database(db_path=os.environ["DB_PATH"])
        new_db.init_db()

        row = new_db.get_url(code)
        assert row is not None
        assert row["original_url"] == "https://persistent.example.com"
        assert row["click_count"] == 2

    def test_multiple_urls_persist_independently(self, client):
        urls = [
            "https://alpha.example.com",
            "https://beta.example.com",
            "https://gamma.example.com",
        ]
        codes = []
        for url in urls:
            res = client.post("/shorten", json={"url": url})
            codes.append(res.json()["short_code"])

        new_db = Database(db_path=os.environ["DB_PATH"])
        for code, url in zip(codes, urls):
            row = new_db.get_url(code)
            assert row is not None
            assert row["original_url"] == url


# --- Validation error shape ---

class TestErrorShape:
    def test_validation_error_returns_422(self, client):
        res = client.post("/shorten", json={"url": "not-a-url"})
        assert res.status_code == 422

    def test_404_has_error_key(self, client):
        res = client.get("/api/stats/xyz123abc")
        data = res.json()
        assert "error" in data

    def test_shorten_validation_error_has_error_key(self, client):
        res = client.post("/shorten", json={"url": ""})
        assert res.status_code == 422
        data = res.json()
        assert "error" in data
