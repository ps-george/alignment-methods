"""Short-code generation."""
from __future__ import annotations

import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # 62 chars
DEFAULT_LEN = 7


def generate_code(length: int = DEFAULT_LEN) -> str:
    """Generate a URL-safe random short code."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
