"""End-to-end tests for the URL shortener API."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path: Path):
    db_path = tmp_path / "test.db"
    app = create_app(db_path=str(db_path))
    with TestClient(app) as c:
        c.db_path = str(db_path)  # type: ignore[attr-defined]
        yield c


def test_shorten_returns_code_and_short_url(client):
    r = client.post("/shorten", json={"url": "https://example.com/foo"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert "code" in body and len(body["code"]) >= 4
    assert body["url"] == "https://example.com/foo"
    assert body["short_url"].endswith("/" + body["code"])


def test_shorten_rejects_invalid_url(client):
    r = client.post("/shorten", json={"url": "not-a-url"})
    assert r.status_code == 422
    body = r.json()
    assert "error" in body
    assert body["error"]["code"] == "validation_error"


def test_shorten_rejects_missing_field(client):
    r = client.post("/shorten", json={})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_shorten_is_idempotent_per_url(client):
    r1 = client.post("/shorten", json={"url": "https://example.com/same"})
    r2 = client.post("/shorten", json={"url": "https://example.com/same"})
    assert r1.json()["code"] == r2.json()["code"]


def test_redirect_returns_302(client):
    r = client.post("/shorten", json={"url": "https://example.com/go"})
    code = r.json()["code"]
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 302
    assert r2.headers["location"] == "https://example.com/go"


def test_redirect_unknown_code_404(client):
    r = client.get("/zzzzzzz", follow_redirects=False)
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "not_found"


def test_stats_unknown_code_404(client):
    r = client.get("/api/stats/zzzzzzz")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_stats_tracks_clicks(client):
    r = client.post("/shorten", json={"url": "https://example.com/track"})
    code = r.json()["code"]

    # initial stats - 0 clicks
    s0 = client.get(f"/api/stats/{code}").json()
    assert s0["clicks"] == 0
    assert s0["url"] == "https://example.com/track"

    # 3 redirects
    for _ in range(3):
        client.get(f"/{code}", follow_redirects=False)

    s1 = client.get(f"/api/stats/{code}").json()
    assert s1["clicks"] == 3


def test_index_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "URL Shortener" in r.text


def test_persistence_across_restart(tmp_path: Path):
    db_path = tmp_path / "persist.db"

    app1 = create_app(db_path=str(db_path))
    with TestClient(app1) as c1:
        r = c1.post("/shorten", json={"url": "https://example.com/persist"})
        assert r.status_code == 201
        code = r.json()["code"]
        # rack up some clicks
        for _ in range(2):
            c1.get(f"/{code}", follow_redirects=False)

    # Simulate restart: brand new app instance against the same file.
    app2 = create_app(db_path=str(db_path))
    with TestClient(app2) as c2:
        s = c2.get(f"/api/stats/{code}").json()
        assert s["url"] == "https://example.com/persist"
        assert s["clicks"] == 2

        # And the redirect still works after restart
        r2 = c2.get(f"/{code}", follow_redirects=False)
        assert r2.status_code == 302
        assert r2.headers["location"] == "https://example.com/persist"

        s2 = c2.get(f"/api/stats/{code}").json()
        assert s2["clicks"] == 3


def test_error_shape_is_consistent(client):
    # 404
    r = client.get("/api/stats/missing")
    assert set(r.json()["error"].keys()) >= {"code", "message"}
    # 422
    r = client.post("/shorten", json={"url": "garbage"})
    assert set(r.json()["error"].keys()) >= {"code", "message"}
