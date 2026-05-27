"""Short-code generation."""
from __future__ import annotations

import secrets
import string

ALPHABET = string.ascii_letters + string.digits  # 62 chars
DEFAULT_LENGTH = 7


def generate(length: int = DEFAULT_LENGTH) -> str:
    """Generate a cryptographically-random short code."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))
