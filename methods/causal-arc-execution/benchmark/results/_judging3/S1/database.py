"""Database layer for URL Shortener using SQLite."""

import logging
import os
import sqlite3
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "urls.db")


class Database:
    """SQLite database wrapper for URL shortener."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Create tables if they don't exist."""
        logger.info("Initializing database at %s", self.db_path)
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS urls (
                    short_code TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    click_count INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        logger.info("Database initialized successfully")

    def create_url(self, short_code: str, original_url: str) -> None:
        """Insert a new URL mapping."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                (short_code, original_url),
            )
            conn.commit()
        logger.debug("Created URL mapping: %s -> %s", short_code, original_url)

    def get_url(self, short_code: str) -> Optional[sqlite3.Row]:
        """Retrieve a URL mapping by short code."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT short_code, original_url, click_count FROM urls WHERE short_code = ?",
                (short_code,),
            ).fetchone()
        return row

    def increment_click(self, short_code: str) -> None:
        """Increment the click count for a short code."""
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
                (short_code,),
            )
            conn.commit()
        logger.debug("Incremented click count for %s", short_code)
