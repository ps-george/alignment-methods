"""SQLite persistence layer for the URL shortener."""
from __future__ import annotations

import logging
import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = os.environ.get("SHORTENER_DB_PATH", "shortener.db")

_lock = threading.Lock()


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


class Database:
    """Thin wrapper around a SQLite connection providing shortener operations."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._conn = _connect(db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        with _lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (
                    code TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    clicks INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with _lock:
            try:
                self._conn.execute("BEGIN")
                yield self._conn
                self._conn.execute("COMMIT")
            except Exception:
                self._conn.execute("ROLLBACK")
                raise

    def insert(self, code: str, url: str) -> None:
        with _lock:
            self._conn.execute(
                "INSERT INTO urls (code, url) VALUES (?, ?)", (code, url)
            )
        logger.info("inserted code=%s", code)

    def get(self, code: str) -> Optional[sqlite3.Row]:
        with _lock:
            cur = self._conn.execute(
                "SELECT code, url, clicks, created_at FROM urls WHERE code = ?",
                (code,),
            )
            return cur.fetchone()

    def increment_clicks(self, code: str) -> None:
        with _lock:
            self._conn.execute(
                "UPDATE urls SET clicks = clicks + 1 WHERE code = ?", (code,)
            )

    def code_exists(self, code: str) -> bool:
        return self.get(code) is not None

    def close(self) -> None:
        with _lock:
            self._conn.close()
