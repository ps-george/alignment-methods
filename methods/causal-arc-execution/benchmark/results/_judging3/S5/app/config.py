"""Runtime configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = os.getenv("SHORTENER_DB_PATH", "data/shortener.db")
    base_url: str = os.getenv("SHORTENER_BASE_URL", "http://localhost:8000")
    code_length: int = int(os.getenv("SHORTENER_CODE_LENGTH", "7"))
    max_collisions: int = 5


def get_settings() -> Settings:
    return Settings()
