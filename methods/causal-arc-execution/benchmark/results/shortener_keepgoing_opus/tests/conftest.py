"""Pytest fixtures."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path so `app` is importable.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import Settings  # noqa: E402
from app.db import Database  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def db_path(tmp_path) -> str:
    return str(tmp_path / "test.db")


@pytest.fixture
def settings(db_path) -> Settings:
    return Settings(
        db_path=db_path,
        base_url="http://testserver",
        code_length=7,
        max_collisions=5,
    )


@pytest.fixture
def app(settings):
    db = Database(settings.db_path)
    return create_app(settings=settings, db=db)


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        # Disable automatic redirect following so we can assert 302 behaviour.
        # Support both newer (follow_redirects) and older (allow_redirects) APIs.
        if hasattr(c, "follow_redirects"):
            c.follow_redirects = False
        yield c
