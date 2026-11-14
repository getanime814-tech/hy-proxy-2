"""Central configuration. Update here when APIs change."""

# ============ AniList ============
ANILIST_URL = "https://graphql.anilist.co"

# ============ Re:ANIME ============
# 🎯 Update this list when Re:ANIME changes domain
# Try domains in order; first working one wins
REANIME_DOMAINS = [
    "https://reanime.cz",   # current primary
    "https://reanime.to",   # fallback
]

# ============ Rate Limits ============
# AniList: 30 requests/min per IP (hard limit)
ANILIST_RATE_MAX = 30
# Re:ANIME: no hard limit; safety cap
REANIME_RATE_MAX = 60
RATE_WINDOW_SECONDS = 60

# ============ HTTP ============
REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3

# ============ User Agents ============
# Rotated per request to reduce fingerprinting
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# ============ Cloudflare TLS Impersonation ============
# curl_cffi impersonate target
TLS_IMPERSONATE = "chrome120"
