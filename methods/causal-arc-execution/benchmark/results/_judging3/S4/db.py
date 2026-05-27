"""SQLite persistence layer for the URL shortener."""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger("shortener.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    code        TEXT PRIMARY KEY,
    original_url TEXT NOT NULL UNIQUE,
    click_count INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class Database:
    def __init__(self, path: Path):
        self._path = path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def initialize(self) -> None:
        logger.debug("Initializing database schema")
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def insert(self, code: str, original_url: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO urls (code, original_url) VALUES (?, ?)",
                (code, original_url),
            )

    def get_by_code(self, code: str) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT code, original_url, click_count FROM urls WHERE code = ?",
                (code,),
            ).fetchone()
        return row

    def get_by_original_url(self, original_url: str) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT code, original_url, click_count FROM urls WHERE original_url = ?",
                (original_url,),
            ).fetchone()
        return row

    def increment_clicks(self, code: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE urls SET click_count = click_count + 1 WHERE code = ?",
                (code,),
            )
