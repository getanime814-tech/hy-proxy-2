"""Shared helpers: HTTP client, rate limiter, UA rotation."""

import asyncio
import logging
import time
from collections import deque
from typing import Optional

from curl_cffi import requests as curl_requests

from config import (
    ANILIST_RATE_MAX,
    REANIME_RATE_MAX,
    RATE_WINDOW_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
    MAX_RETRIES,
    USER_AGENTS,
    TLS_IMPERSONATE,
)

logger = logging.getLogger(__name__)


# ============ RATE LIMITER ============
class RateLimiter:
    """Sliding window rate limiter."""

    def __init__(self, max_requests: int, window: int = RATE_WINDOW_SECONDS):
        self._log: deque = deque()
        self._max = max_requests
        self._window = window

    def check(self) -> bool:
        now = time.time()
        while self._log and now - self._log[0] > self._window:
            self._log.popleft()
        if len(self._log) >= self._max:
            return False
        self._log.append(now)
        return True

    def count(self) -> int:
        now = time.time()
        while self._log and now - self._log[0] > self._window:
            self._log.popleft()
        return len(self._log)


# Global limiter instances
anilist_limiter = RateLimiter(ANILIST_RATE_MAX)
reanime_limiter = RateLimiter(REANIME_RATE_MAX)


# ============ HELPERS ============
def pick_ua() -> str:
    return USER_AGENTS[int(time.time() * 1000) % len(USER_AGENTS)]


async def curl_request(
    url: str,
    method: str = "POST",
    body: Optional[str] = None,
    headers: Optional[dict] = None,
    timeout: int = REQUEST_TIMEOUT_SECONDS,
    max_retries: int = MAX_RETRIES,
):
    """Async wrapper for curl_cffi (Chrome TLS impersonation)."""

    def do_request():
        return curl_requests.request(
            method=method,
            url=url,
            data=body,
            headers=headers,
            impersonate=TLS_IMPERSONATE,
            timeout=timeout,
        )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(do_request)
            if response.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                backoff = (2 ** attempt) * 1.5 + (time.time() % 1)
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} after {backoff:.2f}s "
                    f"— {url} ({response.status_code})"
                )
                await asyncio.sleep(backoff)
                continue
            return response
        except Exception as e:
            last_error = e
            logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1 * (attempt + 1))

    raise last_error or Exception("Max retries exceeded")
