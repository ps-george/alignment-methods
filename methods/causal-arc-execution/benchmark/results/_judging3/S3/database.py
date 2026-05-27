"""SQLite database layer for URL shortener."""

import logging
import os
import sqlite3
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "shortener.db")


class Database:
    """Manages SQLite connection and all DB operations."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        """Create tables if they do not exist."""
        logger.info("Initializing database at %s", self.db_path)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    click_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_code ON urls(code)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_original_url ON urls(original_url)"
            )
            conn.commit()
        logger.info("Database initialized")

    def create_mapping(self, code: str, original_url: str) -> None:
        """Insert a new code -> URL mapping."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO urls (code, original_url) VALUES (?, ?)",
                (code, original_url),
            )
            conn.commit()

    def get_url_by_code(self, code: str) -> Optional[str]:
        """Return the original URL for a given code, or None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT original_url FROM urls WHERE code = ?", (code,)
            ).fetchone()
        return row["original_url"] if row else None

    def get_code_by_url(self, original_url: str) -> Optional[str]:
        """Return the short code for an existing URL, or None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT code FROM urls WHERE original_url = ?", (original_url,)
            ).fetchone()
        return row["code"] if row else None

    def increment_click(self, code: str) -> None:
        """Increment click count for a code."""
        with self._connect() as conn:
            conn.execute(
                "UPDATE urls SET click_count = click_count + 1 WHERE code = ?",
                (code,),
            )
            conn.commit()

    def get_stats(self, code: str) -> Optional[sqlite3.Row]:
        """Return original_url and click_count for a code, or None."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT original_url, click_count FROM urls WHERE code = ?", (code,)
            ).fetchone()
        return row
