import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.db import Database
from app.main import create_app


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


@pytest.fixture
def app_and_db(db_path):
    db = Database(db_path)
    app = create_app(db=db)
    yield app, db
    db.close()


@pytest.fixture
def client(app_and_db):
    app, _ = app_and_db
    with TestClient(app) as c:
        yield c
