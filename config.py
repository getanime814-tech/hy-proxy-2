"""Central configuration. Update here when APIs change."""

import os

# ============ Security ============
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "my-super-secret-key-123")

# ============ AniList ============
ANILIST_URL = "https://graphql.anilist.co"

# ============ Re:ANIME ============
REANIME_DOMAINS = [
    "https://reanime.cz",
]

# ============ Proxies ============
# 🎯 Cloudflare WARP SOCKS5 Proxy
WARP_PROXY = {
    "http": "socks5h://127.0.0.1:40000",
    "https": "socks5h://127.0.0.1:40000"
}

# ============ Rate Limits ============
ANILIST_RATE_MAX = 30
REANIME_RATE_MAX = 60
RATE_WINDOW_SECONDS = 60

# ============ HTTP ============
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
MAX_RETRY_WAIT_SECONDS = 10

# ============ Browser Profiles ============
# curl_cffi auto-generates matching headers based on the impersonation target.
BROWSER_PROFILES = [
    {"name": "chrome124", "impersonate": "chrome124"},
    {"name": "chrome120", "impersonate": "chrome120"},
    {"name": "chrome116", "impersonate": "chrome116"},
]
