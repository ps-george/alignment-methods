"""SQLite persistence layer for the URL shortener."""
from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Tuple

_SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    code        TEXT PRIMARY KEY,
    url         TEXT NOT NULL,
    clicks      INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_urls_url ON urls(url);
"""


class Database:
    """Thin wrapper around sqlite3 with thread-safe access."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        # Ensure parent directory exists when path has one.
        parent = Path(self.path).parent
        if str(parent) not in ("", ".") and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_schema(self) -> None:
        with self._lock, self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def cursor(self) -> Iterator[sqlite3.Cursor]:
        with self._lock:
            conn = self._connect()
            try:
                cur = conn.cursor()
                yield cur
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    # ---- domain operations -------------------------------------------------

    def get_by_url(self, url: str) -> Optional[str]:
        with self.cursor() as cur:
            row = cur.execute(
                "SELECT code FROM urls WHERE url = ? LIMIT 1", (url,)
            ).fetchone()
            return row["code"] if row else None

    def get(self, code: str) -> Optional[Tuple[str, int]]:
        with self.cursor() as cur:
            row = cur.execute(
                "SELECT url, clicks FROM urls WHERE code = ?", (code,)
            ).fetchone()
            if row is None:
                return None
            return row["url"], row["clicks"]

    def insert(self, code: str, url: str) -> None:
        with self.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (code, url) VALUES (?, ?)", (code, url)
            )

    def increment_clicks(self, code: str) -> None:
        with self.cursor() as cur:
            cur.execute(
                "UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,)
            )
