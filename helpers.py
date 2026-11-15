"""Shared helpers: HTTP client, rate limiter, profile rotation."""

import asyncio
import logging
import time
from collections import deque
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional
import random

from curl_cffi import requests as curl_requests
from config import (
    ANILIST_RATE_MAX, REANIME_RATE_MAX, RATE_WINDOW_SECONDS,
    REQUEST_TIMEOUT_SECONDS, MAX_RETRIES, MAX_RETRY_WAIT_SECONDS, BROWSER_PROFILES,
)

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int, window: int = RATE_WINDOW_SECONDS):
        self._log: deque = deque()
        self._max = max_requests
        self._window = window

    def check(self) -> bool:
        now = time.monotonic()
        while self._log and now - self._log[0] > self._window:
            self._log.popleft()
        if len(self._log) >= self._max:
            return False
        self._log.append(now)
        return True

    def count(self) -> int:
        now = time.monotonic()
        while self._log and now - self._log[0] > self._window:
            self._log.popleft()
        return len(self._log)

anilist_limiter = RateLimiter(ANILIST_RATE_MAX)
reanime_limiter = RateLimiter(REANIME_RATE_MAX)

def pick_profile() -> dict:
    if not BROWSER_PROFILES:
        raise ValueError("BROWSER_PROFILES cannot be empty")
    return BROWSER_PROFILES[int(time.monotonic() * 1000) % len(BROWSER_PROFILES)]

def build_html_headers() -> dict:
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "DNT": "1",
    }

def build_api_headers(referer: str) -> dict:
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": referer,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "DNT": "1",
        "Priority": "u=1, i",
    }

def parse_retry_after(header_val: Optional[str], default_wait: float) -> float:
    if not header_val:
        return default_wait
    if header_val.isdigit():
        return min(float(header_val), MAX_RETRY_WAIT_SECONDS)
    try:
        dt = parsedate_to_datetime(header_val)
        wait_time = (dt - datetime.now(dt.tzinfo)).total_seconds()
        return min(max(wait_time, 0), MAX_RETRY_WAIT_SECONDS)
    except Exception:
        return default_wait

async def curl_request(
    url: str,
    method: str = "POST",
    body: Optional[str] = None,
    headers: Optional[dict] = None,
    impersonate: str = "chrome124",
    timeout: int = REQUEST_TIMEOUT_SECONDS,
    max_retries: int = MAX_RETRIES,
    session: Optional[curl_requests.Session] = None,
    proxies: Optional[dict] = None,
):
    max_retries = max(1, max_retries)
    last_error = None

    def do_request(s):
        return s.request(
            method=method,
            url=url,
            data=body,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            proxies=proxies,
        )

    for attempt in range(max_retries):
        is_last_attempt = (attempt == max_retries - 1)
        try:
            if session:
                response = await asyncio.to_thread(do_request, session)
            else:
                with curl_requests.Session(impersonate=impersonate) as s:
                    response = await asyncio.to_thread(do_request, s)
            
            if response.status_code in (429, 503):
                if is_last_attempt:
                    return response
                wait_time = parse_retry_after(response.headers.get("Retry-After"), (2 ** attempt) * 1.5)
                await asyncio.sleep(wait_time)
                continue

            if response.status_code in (500, 502, 504) and not is_last_attempt:
                await asyncio.sleep((2 ** attempt) * 1.5)
                continue

            return response
        except Exception as e:
            last_error = e
            if not is_last_attempt:
                await asyncio.sleep(1 * (attempt + 1))

    raise last_error or Exception("Max retries exceeded without valid response")
