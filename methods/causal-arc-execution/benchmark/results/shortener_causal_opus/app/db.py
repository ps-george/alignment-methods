"""SQLite persistence layer for the URL shortener."""
from __future__ import annotations

import logging
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    code        TEXT PRIMARY KEY,
    url         TEXT NOT NULL,
    clicks      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_urls_url ON urls(url);
"""


class Database:
    """Thin wrapper around sqlite3 with a per-thread connection."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        self._local = threading.local()
        self._init_lock = threading.Lock()
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            self._local.conn = conn
        return conn

    def _init_schema(self) -> None:
        with self._init_lock:
            conn = self._conn()
            conn.executescript(SCHEMA)

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        conn = self._conn()
        try:
            conn.execute("BEGIN IMMEDIATE;")
            yield conn
            conn.execute("COMMIT;")
        except Exception:
            conn.execute("ROLLBACK;")
            raise

    # ---- queries ----
    def get_by_code(self, code: str) -> Optional[sqlite3.Row]:
        cur = self._conn().execute("SELECT * FROM urls WHERE code = ?", (code,))
        return cur.fetchone()

    def get_by_url(self, url: str) -> Optional[sqlite3.Row]:
        cur = self._conn().execute("SELECT * FROM urls WHERE url = ?", (url,))
        return cur.fetchone()

    def insert(self, code: str, url: str) -> None:
        with self.tx() as conn:
            conn.execute("INSERT INTO urls(code, url) VALUES (?, ?)", (code, url))
        log.info("inserted code=%s url=%s", code, url)

    def increment_clicks(self, code: str) -> None:
        with self.tx() as conn:
            conn.execute("UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,))

    def close(self) -> None:
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None
