"""Simple in-memory rate limiter for login attempts.

Not distributed/production-grade — a Redis-backed limiter would be needed once
the app runs across multiple instances — but sufficient to stop naive brute-forcing
of credentials for the MVP. Swappable later without touching auth/routes.py.
"""

import time
from collections import defaultdict

from fastapi import HTTPException, status

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300  # 5 minutes

_attempts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(key: str) -> None:
    """Raises 429 if this key has exceeded MAX_ATTEMPTS within WINDOW_SECONDS."""
    now = time.time()
    _attempts[key] = [t for t in _attempts[key] if now - t < WINDOW_SECONDS]
    if len(_attempts[key]) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again in a few minutes.",
        )


def record_failed_attempt(key: str) -> None:
    _attempts[key].append(time.time())


def reset_attempts(key: str) -> None:
    _attempts.pop(key, None)
