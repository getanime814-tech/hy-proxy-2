"""Shared helpers: HTTP client, rate limiter, profile rotation."""

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
    BROWSER_PROFILES,
)

logger = logging.getLogger(__name__)


# ============ RATE LIMITER ============
class RateLimiter:
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


anilist_limiter = RateLimiter(ANILIST_RATE_MAX)
reanime_limiter = RateLimiter(REANIME_RATE_MAX)


# ============ PROFILE ROTATION ============
def pick_profile() -> dict:
    """Rotate browser profiles to avoid fingerprint tracking."""
    return BROWSER_PROFILES[int(time.time() * 1000) % len(BROWSER_PROFILES)]


def build_browser_headers(profile: dict, referer: str, origin: str) -> dict:
    """Build complete Chrome-like headers (critical for CF bypass)."""
    return {
        "User-Agent": profile["ua"],
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": referer,
        "Origin": origin,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "sec-ch-ua": profile["sec_ch_ua"],
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": profile["platform"],
        "DNT": "1",
        "Priority": "u=1, i",
    }


# ============ CURL CLIENT ============
async def curl_request(
    url: str,
    method: str = "POST",
    body: Optional[str] = None,
    headers: Optional[dict] = None,
    impersonate: str = "chrome124",
    timeout: int = REQUEST_TIMEOUT_SECONDS,
    max_retries: int = MAX_RETRIES,
):
    """Async wrapper for curl_cffi with TLS impersonation."""

    def do_request():
        return curl_requests.request(
            method=method,
            url=url,
            data=body,
            headers=headers,
            impersonate=impersonate,
            timeout=timeout,
            allow_redirects=True,
        )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(do_request)
            # Retry on transient errors only
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
