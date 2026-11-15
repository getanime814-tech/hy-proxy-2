"""Central configuration. Update here when APIs change."""

import os

# ============ Security ============
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "your-super-secret-key-change-me")

# ============ AniList ============
ANILIST_URL = "https://graphql.anilist.co"

# ============ Re:ANIME ============
REANIME_DOMAINS = [
    "https://reanime.cz",
]

# ============ Rate Limits ============
ANILIST_RATE_MAX = 30
REANIME_RATE_MAX = 60
RATE_WINDOW_SECONDS = 60

# ============ HTTP ============
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
MAX_RETRY_WAIT_SECONDS = 10

# ============ Browser Profiles ============
# 🎯 curl_cffi will auto-generate matching User-Agent and sec-ch-ua headers
# based on the impersonate target. Do not manually override them.
BROWSER_PROFILES = [
    {"name": "chrome124", "impersonate": "chrome124"},
    {"name": "chrome120", "impersonate": "chrome120"},
    {"name": "chrome116", "impersonate": "chrome116"},
]
